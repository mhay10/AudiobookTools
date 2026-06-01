#include "open_library.h"

#include "fmt/format.h"

std::string OPL::try_find_book(std::string title, std::vector<std::string> authors, int limit) {
    // Build query string
    std::stringstream ss;
    ss << fmt::format("title:\"{}\" ", title);
    for (auto &author: authors) {
        ss << fmt::format("AND author:\"{}\" ", author);
    }
    std::string query = ss.str();

    // Send API request to Open Library
    httplib::Params params = {
        {"q", query},
        {"limit", std::to_string(limit)}
    };
    auto response = client.Get("/search.json", params, httplib::Headers{});

    // Handle API response
    std::string work;
    if (response && response->status == 200) {
        // TODO: Parse JSON response
    }

    return work;
}

BookInfo OPL::get_book_info(std::string work) {
    return {};
}
