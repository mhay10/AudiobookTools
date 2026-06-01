#pragma once
#include <httplib.h>
#include "bookinfo.h"


class OPL {
    httplib::Client client{"https://openlibrary.org"};

public:
    std::string try_find_book(std::string title, std::vector<std::string> authors, int limit = 1);

    BookInfo get_book_info(std::string work);
};
