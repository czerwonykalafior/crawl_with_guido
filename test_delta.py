from typing import Dict, List
from unittest import TestCase, main


def get_delta(existing: List[int], new: [Dict[str, List[Dict]]]):
    result = {'create': [], 'delete': existing.copy()}

    for item in new:
        if item['id'] < 0:
            result['create'].append(item)
        elif item['id'] in existing:
            result['delete'].remove(item['id'])

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
            self.assertEqual(expected[key], get_delta(self.existing_dict[key], dict_1[key]))

            print(self.existing_dict[key])


if __name__ == '__main__':
    main()
