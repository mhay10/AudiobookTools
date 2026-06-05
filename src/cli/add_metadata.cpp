#include "add_metadata.h"
#include "bookinfo.h"
#include "fmt/base.h"
#include "fmt/ranges.h"
#include "utils/audible.h"
#include "utils/open_library.h"

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
     * - Merge collected data into format (Audible preference over OpenLibrary for everything except description):
     *     {title, authors, narrators, description, publish year}
     * - Write metadata to file (ffmpeg)
     */

    // Get OpenLibrary book info
    BookInfo opl_info;
    std::string work = OPL::try_find_book(title, authors);
    if (!work.empty()) {
        fmt::println("Found match in OpenLibrary: {}", work);
        opl_info = OPL::get_book_info(work);
    }

    // Get Audible book info
    BookInfo audible_info;
    std::string asin = Audible::try_find_book(title, authors, narrators);
    if (!asin.empty()) {
        fmt::println("Found match in Audible: {}", asin);
        audible_info = Audible::get_book_info(asin);
    }

    // Stop if nothing was found
    if (work.empty() && asin.empty()) {
        fmt::println("No match found in OpenLibrary or Audible for: '{}' by '{}'", title, fmt::join(authors, ", "));
        exit(1);
    }

    // Combine info from both sources
    BookInfo book_info;
    book_info.title = !audible_info.title.empty() ? audible_info.title : opl_info.title;
    book_info.authors = !audible_info.authors.empty() ? audible_info.authors : opl_info.authors;
    book_info.narrators = !audible_info.narrators.empty() ? audible_info.narrators : opl_info.narrators;
    book_info.description = !opl_info.description.empty() ? opl_info.description : audible_info.description;
    book_info.year = !audible_info.year.empty() ? audible_info.year : opl_info.year;

    // TODO: Write metadata to file (ffmpeg)
}
