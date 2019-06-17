from common import Dynamic


class Catalog:

    def __init__(self, dsg_api, ksip_api, mine):
        self.__dsg_api = dsg_api
        self.__ksip_api = ksip_api
        self.__mine = mine

        self.__shafts = dict()
        self.__sections = dict()
        self.__locations = dict()
        self.__equipments = dict()
        self.__equipment_types = dict()
        self.__ore_pass = dict()
        self.__skips = dict()
        self.__operators = dict()
        self.__job_kinds = dict()
        self.__units = dict()

        self.__priority = list()

    @staticmethod
    def get_mines(api, date):
        mines_list = api.get_mine(date)
        return Catalog.dict_by_key('idMine', mines_list)

    def __update_shafts(self, date):
        shafts_list = self.__dsg_api.get_shaft(date, self.__mine)
        self.__shafts.update(Catalog.dict_by_key('idShaft', shafts_list))

    def __update_sections(self, date):
        for shaft in self.__shafts.values():
            sections_list = self.__dsg_api.get_section(date, self.__mine, shaft.idShaft)
            self.__sections.update(Catalog.dict_by_key('idSection', sections_list))

    def __update_locations(self, date):
        location_list = self.__dsg_api.get_location(date, self.__mine)
        self.__locations.update(Catalog.dict_by_key('idLocation', location_list))

    def __update_equipment_types(self, date):
        equipment_types_list = self.__dsg_api.get_equipment_type(date)
        self.__equipment_types.update(Catalog.dict_by_key('idEquipmentType', equipment_types_list))

    def __update_equipment(self, date):
        equipment_list = self.__dsg_api.get_equipment(date, self.__mine)
        self.__equipments.update(Catalog.dict_by_key('idEquipment', equipment_list))

    def __update_ore_pass(self, date):
        ore_pass_list = self.__dsg_api.get_orepass(date, self.__mine)
        self.__ore_pass.update(Catalog.dict_by_key('idOrePass', ore_pass_list))

    def __update_skips(self, date):
        skip_list = self.__dsg_api.get_skip(date, self.__mine)
        self.__skips.update(Catalog.dict_by_key('idSkip', skip_list))

    def __update_operators(self, date):
        operators_list = self.__dsg_api.get_operator(date, self.__mine)
        self.__operators.update(Catalog.dict_by_key('idOperator', operators_list))

    def __update_job_kind(self, date):
        job_kind_list = self.__dsg_api.get_job_kind(date, self.__mine)
        self.__job_kinds.update(Catalog.dict_by_key('idJobKind', job_kind_list))

    def __update_unit(self, date):
        unit_list = self.__dsg_api.get_unit(date)
        self.__units.update(Catalog.dict_by_key('idUnit', unit_list))

    def __request_priority(self, date, shift):
        self.__priority = self.__priority + self.__dsg_api.get_priority(date, self.__mine, shift)

    def request_work_orders(self, date, shift):
        self.__request_priority(date, shift)
        work_orders = list()
        for section in self.__sections.values():
            work_orders = work_orders + self.__dsg_api.get_work_order(date, self.__mine, section.idShaft, section.idSection, shift)

        self.__print_work_orders(work_orders)

    def request_locomotive_order(self, date, shift):
        locomotive_orders = self.__dsg_api.get_locomotive_order(date, shift, self.__mine)
        self.__print_locomotive_orders(locomotive_orders)

    def request_skip_order(self, date, shift):
        skip_orders = self.__dsg_api.get_skip_order(date, shift, self.__mine)
        self.__print_skip_orders(skip_orders)

    def request_sdo_fact(self, fact_method, date, shift):
        facts = list()
        for section in self.__sections.values():
            facts = facts + self.__ksip_api.get_fact(fact_method, date, shift, self.__mine, section.idShaft, section.idSection)
        self.__print_facts(facts)

    def request_vgu_fact(self, fact_method, date, shift):
        print('Тут будет метод, который будет запрашивать факт ВШТ и печатать его в приглядном человеку виде:)')

    def update_catalogs(self, date):
        self.__update_shafts(date)
        self.__update_sections(date)
        self.__update_ore_pass(date)
        self.__update_locations(date)
        self.__update_equipment_types(date)
        self.__update_equipment(date)
        self.__update_operators(date)
        self.__update_job_kind(date)
        self.__update_unit(date)
        self.__update_skips(date)

    def __print_facts(self, facts):
        fs = '{0:5s}  {1:5s}  {2:45s}  {3:35s}  {4:45s} {5:25s} {6:25s}  {7}\n'

        print(fs.format(
            'Ш',
            'У',
            'Выработка',
            'Рудоспуск',
            'Вид работ',
            'Тип оборудования',
            'Оборудование',
            'Факт'))

        for fact in facts:
            location_model = self.__locations[fact.idLocation]
            location = Catalog.__item_attr_to_str(self.__locations, location_model.idLocation, 'name')

            ore_pass = Catalog.__item_attr_to_str(self.__ore_pass, fact.idOrePass, 'name')

            section_model = self.__sections[location_model.idSection]
            section = Catalog.__item_attr_to_str(self.__sections, section_model.idSection, 'name', print_id=False)

            shaft = Catalog.__item_attr_to_str(self.__shafts, section_model.idShaft, 'name', print_id=False)

            job_kind = Catalog.__item_attr_to_str(self.__job_kinds, fact.idJobKind, 'name')

            equipment_model = self.__equipments.get(fact.idEquipment, Dynamic(dict()))
            equipment = Catalog.__item_attr_to_str(self.__equipments, fact.idEquipment, 'number')

            equipment_type = Catalog.__item_attr_to_str(self.__equipment_types,
                                                        getattr(equipment_model, 'idEquipmentType', None),
                                                        'name')

            fact_volume = Catalog.__value_to_str(fact.fact)

            print(fs.format(
                shaft,
                section,
                location,
                ore_pass,
                job_kind,
                equipment_type,
                equipment,
                fact_volume))

        print('\n')

    def __print_locomotive_orders(self, locomotive_orders):
        fs = '{0:20s}  {1:45s}  {2:10s}  {3:10s} \n'

        print(fs.format('Электровоз', 'Машинист', 'План', 'Ед. изм'))

        for locomotive_order in locomotive_orders:
            equipment = Catalog.__item_attr_to_str(self.__equipments, locomotive_order.idEquipment, 'number')

            operator = Catalog.__item_attr_to_str(self.__operators, locomotive_order.idOperator, 'name')

            plan = Catalog.__value_to_str(locomotive_order.plan)

            print(fs.format(equipment, operator, plan, 'вагонов'))

        print('\n')

    def __print_skip_orders(self, skip_orders):
        fs = '{0:20s}  {1:45s}  {2:10s}  {3:10s} \n'

        print(fs.format('Рудоспуск', 'Скиповой ствол', 'План', 'Ед. изм'))

        for skip_order in skip_orders:

            ore_pass = Catalog.__item_attr_to_str(self.__ore_pass, skip_order.idSource, 'name')

            skip = Catalog.__item_attr_to_str(self.__skips, skip_order.idDestination, 'name')

            plan = Catalog.__value_to_str(skip_order.plan)

            print(fs.format(ore_pass, skip, plan, 'вагонов'))

        print('\n')

    def __print_work_orders(self, work_orders):

        fs = '{0:5s}  {1:5s}  {2:45s}  {3:30s}  {4:40s}  {5:25s}  {6:25s}  {7:40s}  {8:5s}  {9:10s}  {10:7s}  {11}\n'

        print(fs.format(
                'Ш',
                'У',
                'Выработка',
                'Рудоспуск',
                'Вид работ',
                'Тип оборудования',
                'Оборудование',
                'Оператор',
                'План',
                'Ед. изм',
                'Порядок',
                'Доп. инф.'))

        for work_order in work_orders:
            location_model = self.__locations[work_order.idLocation]
            location = Catalog.__item_attr_to_str(self.__locations, location_model.idLocation, 'name')

            ore_pass = Catalog.__item_attr_to_str(self.__ore_pass, work_order.idOrePass, 'name')

            section_model = self.__sections[location_model.idSection]
            section = Catalog.__item_attr_to_str(self.__sections, section_model.idSection, 'name', print_id=False)

            shaft = Catalog.__item_attr_to_str(self.__shafts, section_model.idShaft, 'name', print_id=False)

            job_kind = Catalog.__item_attr_to_str(self.__job_kinds, work_order.idJobKind, 'name')

            equipment_type = Catalog.__item_attr_to_str(self.__equipment_types, work_order.idEquipmentType, 'name')

            equipment = Catalog.__item_attr_to_str(self.__equipments, work_order.idEquipment, 'number')

            operator = Catalog.__item_attr_to_str(self.__operators, work_order.idOperator, 'name')

            plan = Catalog.__value_to_str(work_order.plan)

            unit = Catalog.__item_attr_to_str(self.__units, work_order.idUnit, 'name', print_id=False)

            order = Catalog.__value_to_str(work_order.order)

            description = Catalog.__value_to_str(work_order.description)

            print(fs.format(
                        shaft,
                        section,
                        location,
                        ore_pass,
                        job_kind,
                        equipment_type,
                        equipment,
                        operator,
                        plan,
                        unit,
                        order,
                        description))

        print('\n')

    @staticmethod
    def __item_attr_to_str(items, item_id, attr, print_id=True):
        if item_id is not None and item_id in items:
            if print_id:
                item_str = '({0}) '.format(str(item_id)) + getattr(items[item_id], attr)
            else:
                item_str = getattr(items[item_id], attr)
        else:
            item_str = '-'

        return item_str

    @staticmethod
    def __value_to_str(value):
        if value is not None:
            value_str = str(value)
        else:
            value_str = '-'

        return value_str

    @staticmethod
    def dict_by_key(key, items):
        return dict((getattr(item, key), item) for item in items)



