// ============================================================
//  wake_server.h — HTTP Server kecil di ESP32
//  Endpoint:
//    GET/POST /wake        — bangunkan Xiaozhi
//    POST     /say         — kirim teks perintah ke Xiaozhi AI
//    GET      /status      — cek status ESP32
// ============================================================

#pragma once

#include <esp_http_server.h>
#include <esp_log.h>
#include <cJSON.h>
#include <functional>
#include <string>

#define WAKE_SERVER_TAG "WakeServer"
#define WAKE_SERVER_PORT 8080

class WakeServer {
public:
    static WakeServer& GetInstance() {
        static WakeServer instance;
        return instance;
    }

    WakeServer(const WakeServer&) = delete;
    WakeServer& operator=(const WakeServer&) = delete;

    void SetWakeCallback(std::function<void(const std::string&)> cb) {
        wake_callback_ = cb;
    }

    void SetSayCallback(std::function<void(const std::string&)> cb) {
        say_callback_ = cb;
    }

    bool Start() {
        if (server_ != nullptr) {
            ESP_LOGW(WAKE_SERVER_TAG, "Server already running");
            return true;
        }

        httpd_config_t config = HTTPD_DEFAULT_CONFIG();
        config.server_port = WAKE_SERVER_PORT;
        config.lru_purge_enable = true;

        if (httpd_start(&server_, &config) != ESP_OK) {
            ESP_LOGE(WAKE_SERVER_TAG, "Failed to start HTTP server");
            return false;
        }

        // GET /wake
        httpd_uri_t wake_get = {
            .uri      = "/wake",
            .method   = HTTP_GET,
            .handler  = WakeGetHandler,
            .user_ctx = this
        };
        httpd_register_uri_handler(server_, &wake_get);

        // POST /wake
        httpd_uri_t wake_post = {
            .uri      = "/wake",
            .method   = HTTP_POST,
            .handler  = WakePostHandler,
            .user_ctx = this
        };
        httpd_register_uri_handler(server_, &wake_post);

        // POST /say
        httpd_uri_t say_post = {
            .uri      = "/say",
            .method   = HTTP_POST,
            .handler  = SayPostHandler,
            .user_ctx = this
        };
        httpd_register_uri_handler(server_, &say_post);

        // GET /status
        httpd_uri_t status_get = {
            .uri      = "/status",
            .method   = HTTP_GET,
            .handler  = StatusHandler,
            .user_ctx = this
        };
        httpd_register_uri_handler(server_, &status_get);

        ESP_LOGI(WAKE_SERVER_TAG, "HTTP Wake Server started on port %d", WAKE_SERVER_PORT);
        ESP_LOGI(WAKE_SERVER_TAG, "Endpoints:");
        ESP_LOGI(WAKE_SERVER_TAG, "  GET/POST http://192.168.1.10:%d/wake", WAKE_SERVER_PORT);
        ESP_LOGI(WAKE_SERVER_TAG, "  POST     http://192.168.1.10:%d/say", WAKE_SERVER_PORT);
        ESP_LOGI(WAKE_SERVER_TAG, "  GET      http://192.168.1.10:%d/status", WAKE_SERVER_PORT);
        return true;
    }

    void Stop() {
        if (server_ != nullptr) {
            httpd_stop(server_);
            server_ = nullptr;
        }
    }

private:
    WakeServer() = default;
    ~WakeServer() { Stop(); }

    httpd_handle_t server_ = nullptr;
    std::function<void(const std::string&)> wake_callback_;
    std::function<void(const std::string&)> say_callback_;

    static esp_err_t SendJson(httpd_req_t *req, const char* json) {
        httpd_resp_set_type(req, "application/json");
        httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
        httpd_resp_send(req, json, strlen(json));
        return ESP_OK;
    }

    static std::string ReadBody(httpd_req_t *req) {
        char buf[256] = {0};
        int ret = httpd_req_recv(req, buf, sizeof(buf) - 1);
        if (ret > 0) {
            buf[ret] = '\0';
            return std::string(buf);
        }
        return "";
    }

    static esp_err_t WakeGetHandler(httpd_req_t *req) {
        auto* self = (WakeServer*)req->user_ctx;
        ESP_LOGI(WAKE_SERVER_TAG, "GET /wake");
        if (self->wake_callback_) self->wake_callback_("Hi ESP");
        return SendJson(req, "{\"status\":\"ok\",\"action\":\"wake\"}");
    }

    static esp_err_t WakePostHandler(httpd_req_t *req) {
        auto* self = (WakeServer*)req->user_ctx;
        std::string body = ReadBody(req);
        std::string wake_word = "Hi ESP";

        if (!body.empty()) {
            auto* json = cJSON_Parse(body.c_str());
            if (json) {
                auto* ww = cJSON_GetObjectItem(json, "wake_word");
                if (cJSON_IsString(ww)) wake_word = ww->valuestring;
                cJSON_Delete(json);
            }
        }

        ESP_LOGI(WAKE_SERVER_TAG, "POST /wake — wake_word: %s", wake_word.c_str());
        if (self->wake_callback_) self->wake_callback_(wake_word);
        return SendJson(req, "{\"status\":\"ok\",\"action\":\"wake\"}");
    }

    static esp_err_t SayPostHandler(httpd_req_t *req) {
        auto* self = (WakeServer*)req->user_ctx;
        std::string body = ReadBody(req);
        std::string text;

        if (!body.empty()) {
            auto* json = cJSON_Parse(body.c_str());
            if (json) {
                auto* t = cJSON_GetObjectItem(json, "text");
                if (cJSON_IsString(t)) text = t->valuestring;
                cJSON_Delete(json);
            }
        }

        if (text.empty()) {
            return SendJson(req, "{\"status\":\"error\",\"message\":\"text is required\"}");
        }

        ESP_LOGI(WAKE_SERVER_TAG, "POST /say — text: %s", text.c_str());
        if (self->say_callback_) self->say_callback_(text);
        return SendJson(req, "{\"status\":\"ok\",\"action\":\"say\"}");
    }

    static esp_err_t StatusHandler(httpd_req_t *req) {
        return SendJson(req,
            "{\"status\":\"ok\",\"device\":\"xiaozhi-esp32\","
            "\"mac\":\"3c:dc:75:6b:f9:ec\","
            "\"endpoints\":[\"/wake\",\"/say\",\"/status\"]}");
    }
};