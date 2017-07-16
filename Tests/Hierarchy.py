import uuid
import unittest

from Services.RESTService import RESTService
from Services.LoginService import LoginService
from Services.DimensionService import DimensionService
from Services.HierarchyService import HierarchyService
from Objects.Dimension import Dimension
from Objects.Hierarchy import Hierarchy


# Configuration for tests
port = 8001
user = 'admin'
pwd = 'apple'
dimension_prefix = 'TM1py_unittest_dimension_{}'


class TestHierarchyMethods(unittest.TestCase):
    login = LoginService.native(user, pwd)
    tm1_rest = RESTService(ip='', port=port, login=login, ssl=False)

    dimension_service = DimensionService(tm1_rest)
    hierarchy_service = HierarchyService(tm1_rest)

    dimension_name = dimension_prefix.format(uuid.uuid4())

    # create dimension with a default hierarchy
    def test1_create(self):
        d = Dimension(self.dimension_name)
        h = Hierarchy(self.dimension_name, self.dimension_name)
        h.add_element('Total Years', 'Consolidated')
        h.add_element('No Year', 'Numeric')
        h.add_element('1989', 'Numeric')
        h.add_element_attribute('Previous Year', 'String')
        h.add_element_attribute('Next Year', 'String')
        h.add_edge('Total Years', '1989', 2)
        d.add_hierarchy(h)
        self.dimension_service.create(d)

    def test2_get(self):
        d = self.dimension_service.get(dimension_name=self.dimension_name)
        h = d.default_hierarchy
        self.assertIn('Total Years', h.elements.keys())
        self.assertIn('No Year', h.elements.keys())
        self.assertIn('1989', h.elements.keys())
        self.assertIn('Next Year', [ea.name for ea in h.element_attributes])
        self.assertIn('Previous Year', [ea.name for ea in h.element_attributes])

    def test3_update(self):
        # Get dimension and hierarchy
        d = self.dimension_service.get(dimension_name=self.dimension_name)
        h = d.default_hierarchy
        # Edit Elements and Edges
        for year in range(2010, 2021, 1):
            parent = str(year)
            h.add_element(parent, 'Consolidated')
            h.add_edge('Total Years', parent, 1)
            for month in ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'):
                component = '{}-{}'.format(year, month)
                h.add_element(component, 'Numeric')
                h.add_edge(parent, component, 1)
        # Edit Element Attributes
        h.add_element_attribute('Name Long', 'Alias')
        h.add_element_attribute('Name Short', 'Alias')
        h.add_element_attribute('Days', 'Numeric')
        # Remove attribute
        h.remove_element_attribute('Next Year')
        # Remove Edge
        h.remove_edge('Total Years', '1989')
        # Update Edge
        h.update_edge('Total Years', '2011', 2)
        # Update_element
        h.update_element('No Year', 'String')
        self.dimension_service.update(d)

        # Check if update workes
        d = self.dimension_service.get(self.dimension_name)
        h = d.default_hierarchy
        self.assertIn('2010-Jan', h.elements.keys())
        self.assertIn('2020-Dec', h.elements.keys())

        self.assertNotIn('Next Year', [ea.name for ea in h.element_attributes])
        self.assertIn('Previous Year', [ea.name for ea in h.element_attributes])
        self.assertIn('Days', [ea.name for ea in h.element_attributes])
        self.assertIn('Name Long', [ea.name for ea in h.element_attributes])

        self.assertEqual(h.edges[('Total Years', '2011')], 2)
        self.assertEqual(h.elements['No Year'].element_type, 'String')

    def test4_test_delete(self):
        self.dimension_service.delete(self.dimension_name)

    def test5_logout(self):
        self.tm1_rest.logout()

