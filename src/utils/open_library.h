#pragma once
#include <httplib.h>
#include "bookinfo.h"


class OPL {
    inline static httplib::Client client{"https://openlibrary.org"};

public:
    static std::string try_find_book(std::string title, std::vector<std::string> authors);

    static BookInfo get_book_info(std::string work);
};
