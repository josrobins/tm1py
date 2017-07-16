import re

from Services.RESTService import RESTService
from Services.LoginService import LoginService
from Services.CubeService import CubeService
from Services.DimensionService import DimensionService
from Services.ViewService import ViewService
from Services.SubsetService import SubsetService
from Services.ProcessService import ProcessService


login = LoginService.native('admin', 'apple')

with RESTService(ip='', port=8001, login=login, ssl=False) as tm1_rest:
    cube_service = CubeService(tm1_rest)
    dimension_service = DimensionService(tm1_rest)
    subset_service = SubsetService(tm1_rest)
    view_service = ViewService(tm1_rest)
    process_service = ProcessService(tm1_rest)

    # regular expression for everything that starts with 'temp_', 'test' or 'TM1py'
    regex_list = ['^temp_*', '^test*', '^TM1py*']

    # iterate through cubes
    cubes = cube_service.get_all_names()
    for cube in cubes:
        for regex in regex_list:
            if re.match(regex, cube, re.IGNORECASE):
                cube_service.delete(cube)
                break
            else:
                private_views, public_views = view_service.get_all(cube_name=cube)
                for view in private_views:
                    if re.match(regex, view.name, re.IGNORECASE):
                        view_service.delete(cube_name=cube, view_name=view.name, private=True)
                for view in public_views:
                    if re.match(regex, view.name, re.IGNORECASE):
                        view_service.delete(cube_name=cube, view_name=view.name, private=False)

    # iterate through dimensions
    dimensions = dimension_service.get_all_names()
    for dimension in dimensions:
        for regex in regex_list:
            if re.match(regex, dimension, re.IGNORECASE):
                dimension_service.delete(dimension)
                break
            else:
                subsets = subset_service.get_all_names(dimension_name=dimension, hierarchy_name=dimension)
                for subset in subsets:
                    if re.match(regex, subset, re.IGNORECASE):
                        subset_service.delete(dimension, subset)

    # iterate through Processes
    processes = process_service.get_all_names()
    for process in processes:
        for regex in regex_list:
            if re.match(regex, process, re.IGNORECASE):
                process_service.delete(process)

