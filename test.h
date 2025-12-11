#ifndef TEST_H
#define TEST_H

#include <vector>
#include <algorithm>

#define TEST_BASE 66300

enum TESTToDo {
    test_2,    test_3,    test_END,    test_START};

class TEST : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    TEST(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(26, 8);
        SetUpFarmCategoryInformation();
    }
};

#endif