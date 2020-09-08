from typing import Dict, List
from unittest import TestCase, main


def get_delta(existing: List[int], new: [Dict[str, List[Dict]]]):
    result = dict()
    result['create'] = [item for item in new if item['id'] < 0]

    result['delete'] = existing

    for idx, existing_id in enumerate(existing):
        for new_item in new:
            if existing_id == new_item['id']:
                result['delete'].pop(idx)

    return result


class DeltaTestCase(TestCase):
    def setUp(self) -> None:
        self.existing_dict = {
            'nodes': [1, 2],
            'functions': [1, 2],
            'edges': [1]
        }

    def test_basic(self):
        dict_1 = {
            'nodes': [
                {'id': 1, 'name': 'node1'},
                {'id': -1, 'name': 'node3'},
            ],
            'functions': [
                {'id': 1, 'name': 'name1', 'node': 1},
                {'id': -1, 'name': 'name3', 'node': -1},
            ],
            'edges': [
                {'id': -1, 'name': 'name3', 'source': 1, 'target': -1},
            ]
        }
        expected = {
            'nodes': {
                'create': [{'id': -1, 'name': 'node3'}],
                'delete': [2],
            },
            'functions': {
                'create': [{'id': -1, 'name': 'name3', 'node': -1}],
                'delete': [2],
            },
            'edges': {
                'create': [{'id': -1, 'name': 'name3', 'source': 1, 'target': -1}],
                'delete': [1],
            },
        }

        for key, value in dict_1.items():
            self.assertEqual(get_delta(self.existing_dict[key], dict_1[key]), expected[key])


if __name__ == '__main__':
    main()
