#include "open_library.h"
#include "nlohmann/json.hpp"
#include "fmt/format.h"

using json = nlohmann::json;

std::string OPL::try_find_book(std::string title, std::vector<std::string> authors) {
    // Build query string
    std::stringstream ss;
    ss << fmt::format("title:\"{}\" ", title);
    for (auto &author: authors) {
        ss << fmt::format("AND author:\"{}\" ", author);
    }
    std::string query = ss.str();

    // Send API request for search results
    httplib::Params params = {
        {"q", query},
        {"limit", "1"},
    };
    auto response = client.Get("/search.json", params, httplib::Headers{});

    // Try to parse work key from API response
    std::string work;
    if (response && response->status == 200) {
        json data = json::parse(response->body);
        if (data["num_found"] > 0) {
            std::string key = data["docs"][0]["key"];
            work = key.substr(key.find("/works/") + 7);
        }
    }

    return work;
}

BookInfo OPL::get_book_info(std::string work) {
    // Send API request for title, authors, and publish year
    httplib::Params params = {
        {"q", fmt::format("/works/{}", work)},
        {"limit", "1"},
        {"fields", "title,author_name,first_publish_year"}
    };
    auto response = client.Get("/search.json", params, httplib::Headers{});

    // Put relevant data in standard format
    BookInfo info;
    if (response && response->status == 200) {
        json data = json::parse(response->body);
        if (data["num_found"] > 0) {
            auto doc = data["docs"][0];
            info.title = doc["title"].get<std::string>();
            info.authors = doc["author_name"].get<std::vector<std::string> >();
            info.year = std::to_string(doc["first_publish_year"].get<int>());
        }
    }

    // Send API request for description
    response = client.Get(fmt::format("/works/{}.json", work));

    // Add description to standard format
    if (response && response->status == 200) {
        json data = json::parse(response->body);
        if (data.contains("description")) {
            info.description = data["description"].get<std::string>();
        }
    }

    return info;
}
