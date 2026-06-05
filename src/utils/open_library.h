#pragma once
#include "bookinfo.h"


class OPL {
    inline static const std::string OPENLIBRARY_API = "https://openlibrary.org";

public:
    static std::string try_find_book(std::string title, std::vector<std::string> authors);

    static BookInfo get_book_info(std::string work);
};
