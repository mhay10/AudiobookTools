#pragma once
#include "bookinfo.h"
#include "fmt/base.h"

class Audible {
    inline static const std::string AUDIBLE_API = "https://api.audible.com/1.0";
    inline static const std::string AUDNEXUS_API = "https://api.audnex.us";

public:
    static std::string try_find_book(std::string title, std::vector<std::string> authors,
                                     std::vector<std::string> narrators = {});

    static BookInfo get_book_info(std::string asin);
};
