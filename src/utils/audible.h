#pragma once
#include "bookinfo.h"
#include "httplib.h"

class Audible {
    inline static httplib::Client catalog{"https://api.audible.com/1.0"};
    inline static httplib::Client audnexus{"https://api.audnexus.com"};

public:
    static std::string try_find_book(std::string title, std::vector<std::string> authors,
                                     std::vector<std::string> narrators = {});

    static BookInfo get_book_info(std::string asin);
};
