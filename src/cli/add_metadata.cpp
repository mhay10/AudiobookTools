#include "add_metadata.h"
#include <fmt/base.h>
#include "fmt/ranges.h"

// Standardized book metadata
struct BookInfo {
    std::string title;
    std::vector<std::string> authors;
    std::vector<std::string> narrators;
    std::string description;
    std::string year;
};

// Helper function declarations
namespace {
    std::string search_openlibrary_catalog(std::string title, std::vector<std::string> authors);

    BookInfo get_openlibrary_data(std::string work);

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
    if (!work.empty()) {
        fmt::println("Found book in OpenLibrary: {}", work);
        // TODO: Get book data from OpenLibrary
    }

    std::string asin = search_audible_catalog(title, authors, narrators);
    if (!asin.empty()) {
        fmt::println("Found book in Audible: {}", asin);
        // TODO: Get book data from Audible
    }
}

namespace {
    std::string search_openlibrary_catalog(std::string title, std::vector<std::string> authors) {
        return "";
    }

    std::string search_audible_catalog(std::string asin, std::vector<std::string> authors,
                                       std::vector<std::string> narrators) {
        return "";
    }

    BookInfo get_openlibrary_data(std::string work) {
        return {};
    }

    BookInfo get_audible_data(std::string asin) {
        return {};
    }
}
