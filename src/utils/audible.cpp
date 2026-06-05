#include "audible.h"
#include <cpr/cpr.h>
#include <nlohmann/json.hpp>
#include "fmt/xchar.h"

using json = nlohmann::json;

std::string Audible::try_find_book(std::string title, std::vector<std::string> authors,
                                   std::vector<std::string> narrators) {
    // Build query params
    cpr::Parameters params = {
        {"title", title},
        {"author", fmt::to_string(fmt::join(authors, ","))},
        {"num_results", "1"}
    };
    if (!narrators.empty()) {
        params.Add({"narrator", fmt::to_string(fmt::join(narrators, ","))});
    }

    // Send API request for search results
    auto response = cpr::Get(cpr::Url{AUDIBLE_API + "/catalog/products"}, params);

    // Try to parse ASIN from API response
    std::string asin;
    if (response.status_code == 200) {
        json data = json::parse(response.text);
        if (data["total_results"] > 0) {
            asin = data["products"][0]["asin"].get<std::string>();
        }
    }

    return asin;
}

BookInfo Audible::get_book_info(std::string asin) {
    // Send API request for book data
    auto response = cpr::Get(cpr::Url{AUDNEXUS_API + fmt::format("/books/{}", asin)});

    // Put relevant data in standard format
    BookInfo info;
    if (response.status_code == 200 || response.status_code == 304) {
        json data = json::parse(response.text);

        // Add single data points
        if (data.contains("title")) info.title = data["title"].get<std::string>();
        if (data.contains("copyright")) info.year = std::to_string(data["copyright"].get<int>());
        if (data.contains("summary")) info.description = data["summary"].get<std::string>();

        // Add authors and narrators
        if (data.contains("authors")) {
            for (auto &author: data["authors"]) {
                info.authors.push_back(author["name"].get<std::string>());
            }
        }
        if (data.contains("narrators")) {
            for (auto &narrator: data["narrators"]) {
                info.narrators.push_back(narrator["name"].get<std::string>());
            }
        }
    }

    return info;
}
