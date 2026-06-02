#include "add_metadata.h"
#include "bookinfo.h"
#include "fmt/base.h"
#include "fmt/ranges.h"
#include "httplib.h"
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
     * - Merge collected data into format (OpenLibrary preference):
     *     {title, authors, narrators, description, publish year}
     * - Write metadata to file (ffmpeg)
     */

    BookInfo opl_info;
    std::string work = OPL::try_find_book(title, authors);
    if (!work.empty()) {
        fmt::println("Found book in OpenLibrary: {}", work);
        opl_info = OPL::get_book_info(work);
    }

    std::string asin = Audible::try_find_book(title, authors, narrators);
    if (!asin.empty()) {
        fmt::println("Found book in Audible: {}", asin);
        // TODO: Get book data from Audible
    }

    if (work.empty() && asin.empty()) {
        fmt::println("No match found in OpenLibrary or Audible for: '{}' by '{}'", title, fmt::join(authors, ", "));
        exit(1);
    }
}
