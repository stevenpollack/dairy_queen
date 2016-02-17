from doubledip import FlatList

class TestFlatList:

    def test_init(self):

        assert FlatList(1) == FlatList([1])
        assert FlatList([1]) == [1]

        # double dips should be flat, upon instantiation
        assert FlatList([1, [2]]) == [1, 2]

        # instantiation should be idempotent
        assert FlatList(FlatList([1, [2]])) == [1, 2]

        assert FlatList({'a': 1}) == [{'a': 1}]

    def test_prepend(self):
        l = FlatList([1])
        l.prepend(2)
        assert l == [2, 1]

    def test_flatten(self):
        l = FlatList([1, [2, [3]]])
        assert l.flatten() == [1, 2, 3]
        assert l == [1, 2, 3]


    def test_flat_append(self):
        l = FlatList([1])
        l.flat_append([2])
        assert l == [1, 2]
        assert l.flat_append(3) == [1, 2, 3]

    def test_flat_prepend(self):
        l = FlatList([1])
        l.flat_prepend([2])
        assert l == [2, 1]
        assert l.flat_prepend(3) == [3, 2, 1]
