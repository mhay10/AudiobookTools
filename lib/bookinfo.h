#pragma once
#include <string>
#include <vector>

struct BookInfo {
    std::string title;
    std::vector<std::string> authors;
    std::vector<std::string> narrators;
    std::string description;
    std::string year;
};
