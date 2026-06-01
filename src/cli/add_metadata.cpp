#include "add_metadata.h"

#include "bookinfo.h"
#include "fmt/base.h"
#include "fmt/ranges.h"
#include "httplib.h"

// Standardized book metadata

// Helper function declarations
namespace {
    std::string search_openlibrary_catalog(std::string title, std::vector<std::string> authors);

    // BookInfo get_openlibrary_data(std::string work);

    std::string search_audible_catalog(std::string title, std::vector<std::string> authors,
                                       std::vector<std::string> narrators);

    BookInfo get_audible_data(std::string asin);
}

void AddMetadata::run() {
    /* Process:
     * - Check OpenLibrary for book if it exists (OpenLibrary API - Book Search)
     * - If yes, get info from OpenLibrary (OpenLibrary API - Work & Edition)
     *
     * - Check Audible for book if it exists (Audible Catalog API)
     * - If yes, get info from audible (Audnexus API)
     *
     * - Stop execution if no data found from either source
     *
     * - Merge collected data into format (OpenLibrary preference):
     *     {title, authors, narrators, description, publish year}
     * - Write metadata to file (ffmpeg)
     */

    std::string work = search_openlibrary_catalog(title, authors);
    bool found_in_openlibrary = !work.empty();
    if (found_in_openlibrary) {
        fmt::println("Found book in OpenLibrary: {}", work);
        // TODO: Get book data from OpenLibrary
    }

    std::string asin = search_audible_catalog(title, authors, narrators);
    bool found_in_audible = !asin.empty();
    if (found_in_audible) {
        fmt::println("Found book in Audible: {}", asin);
        // TODO: Get book data from Audible
    }

    if (!found_in_audible && !found_in_openlibrary) {
        fmt::println("No match found in OpenLibrary or Audible for: '{}' by '{}'", title, fmt::join(authors, ", "));
        exit(1);
    }
}

namespace {
    std::string search_openlibrary_catalog(std::string title, std::vector<std::string> authors) {
        // API Url: https://openlibrary.org/search.json?q={}&limit=1
        // q format: title:" " AND author:" " AND author:" " ...

        // Build query string
        std::stringstream ss;
        ss << fmt::format("title:\"{}\"", title);
        for (auto &author: authors) {
            ss << fmt::format(" AND author:\"{}\"", author);
        }
        std::string query = ss.str();

        fmt::println("Searching OpenLibrary with query: {}", query);

        httplib::Client req("https://openlibrary.org");
        httplib::Params params = {
            {"q", query},
            {"limit", "1"}
        };
        auto response = req.Get("/search.json", params, httplib::Headers{});
        if (response && response->status == 200) {
            fmt::println("{}", response->body);
        }

        return "";
    }

    std::string search_audible_catalog(std::string asin, std::vector<std::string> authors,
                                       std::vector<std::string> narrators) {
        return "";
    }

    // BookInfo get_openlibrary_data(std::string work) {
    //     return {};
    // }
    //
    // BookInfo get_audible_data(std::string asin) {
    //     return {};
    // }
}
