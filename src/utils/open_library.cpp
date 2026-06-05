#include "open_library.h"
#include "nlohmann/json.hpp"
#include "fmt/format.h"
#include "cpr/cpr.h"

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
    cpr::Parameters params = {
        {"q", query},
        {"limit", "1"},
    };
    auto response = cpr::Get(cpr::Url{OPENLIBRARY_API + "/search.json"}, params);

    // Try to parse work key from API response
    std::string work;
    if (response.status_code == 200) {
        json data = json::parse(response.text);
        if (data["num_found"] > 0) {
            std::string key = data["docs"][0]["key"];
            work = key.substr(key.find("/works/") + 7);
        }
    }

    return work;
}

BookInfo OPL::get_book_info(std::string work) {
    // Send API request for title, authors, and publish year
    cpr::Parameters params = {
        {"q", fmt::format("/works/{}", work)},
        {"limit", "1"},
        {"fields", "title,author_name,first_publish_year"}
    };
    auto response = cpr::Get(cpr::Url{OPENLIBRARY_API + "/search.json"}, params);

    // Put relevant data in standard format
    BookInfo info;
    if (response.status_code == 200) {
        json data = json::parse(response.text);
        if (data["num_found"] > 0) {
            auto doc = data["docs"][0];
            info.title = doc["title"].get<std::string>();
            info.authors = doc["author_name"].get<std::vector<std::string> >();
            info.year = std::to_string(doc["first_publish_year"].get<int>());
        }
    }

    // Send API request for description
    response = cpr::Get(cpr::Url{OPENLIBRARY_API + fmt::format("/works/{}.json", work)});

    // Add description to standard format
    if (response.status_code == 200) {
        json data = json::parse(response.text);
        if (data.contains("description")) {
            info.description = data["description"].get<std::string>();
        }
    }

    return info;
}
