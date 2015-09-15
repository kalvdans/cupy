import mock
import unittest

import numpy
import six

from chainer.testing import condition
from chainer.testing import hypothesis_testing
from cupy import cuda
from cupy import random
from cupy import testing


@testing.gpu
class TestRandint(unittest.TestCase):

    _multiprocess_can_split_ = True

    def setUp(self):
        self.rs_tmp = random.generator._random_states
        device_id = cuda.Device().id
        self.m = mock.Mock()
        self.m.interval.return_value = 0
        random.generator._random_states = {device_id: self.m}

    def tearDown(self):
        random.generator._random_states = self.rs_tmp

    def test_value_error(self):
        with self.assertRaises(ValueError):
            random.randint(100, 1)

    def test_high_and_size_are_none(self):
        random.randint(3)
        self.m.interval.assert_called_with(2, None)

    def test_size_is_none(self):
        random.randint(3, 5)
        self.m.interval.assert_called_with(1, None)

    def test_high_is_none(self):
        random.randint(3, None, (1, 2, 3))
        self.m.interval.assert_called_with(2, (1, 2, 3))

    def test_no_none(self):
        random.randint(3, 5, (1, 2, 3))
        self.m.interval.assert_called_with(1, (1, 2, 3))


class TestRandint2(unittest.TestCase):

    def setUp(self):
        self.rs_tmp = random.generator._random_states
        random.generator._random_states = {}

    def tearDown(self):
        random.generator._random_states = self.rs_tmp

    @condition.repeat(10)
    def test_within_interval(self):
        val = random.randint(0, 10).get()
        self.assertLessEqual(0, val)
        self.assertLess(val, 10)

    @condition.retry(20)
    def test_lower_bound(self):
        val = random.randint(0, 3).get()
        self.assertEqual(0, val)

    @condition.retry(20)
    def test_upper_bound(self):
        val = random.randint(0, 3).get()
        self.assertEqual(2, val)

    @condition.retry(5)
    def test_goodness_of_fit(self):
        mx = 5
        trial = 100
        vals = [random.randint(mx).get() for _ in six.moves.xrange(trial)]
        counts = numpy.histogram(vals, bins=numpy.arange(mx + 1))[0]
        expected = numpy.array([float(trial) / mx] * mx)
        if not hypothesis_testing.chi_square_test(counts, expected):
            self.fail()


@testing.gpu
class TestRandomIntegers(unittest.TestCase):

    _multiprocess_can_split_ = True

    def setUp(self):
        self.randint_tmp = random.sample_.randint
        random.sample_.randint = mock.Mock()

    def tearDown(self):
        random.sample_.randint = self.randint_tmp

    def test_normal(self):
        random.random_integers(3, 5)
        random.sample_.randint.assert_called_with(3, 6, None)

    def test_high_is_none(self):
        random.random_integers(3, None)
        random.sample_.randint.assert_called_with(1, 4, None)

    def test_size_is_not_none(self):
        random.random_integers(3, 5, (1, 2, 3))
        random.sample_.randint.assert_called_with(3, 6, (1, 2, 3))


@testing.gpu
class TestRandomIntegers2(unittest.TestCase):

    _multiprocess_can_split_ = True

    def setUp(self):
        self.rs_tmp = random.generator._random_states
        random.generator._random_states = {}

    def tearDown(self):
        random.generator._random_states = self.rs_tmp

    @condition.repeat(10)
    def test_within_interval(self):
        val = random.random_integers(0, 10).get()
        self.assertLessEqual(0, val)
        self.assertLessEqual(val, 10)

    @condition.retry(20)
    def test_lower_bound(self):
        val = random.random_integers(0, 3).get()
        self.assertEqual(0, val)

    @condition.retry(20)
    def test_upper_bound(self):
        val = random.random_integers(0, 3).get()
        self.assertEqual(3, val)

    @condition.retry(5)
    def test_goodness_of_fit(self):
        mx = 5
        trial = 100
        vals = [random.randint(0, mx).get() for _ in six.moves.xrange(trial)]
        counts = numpy.histogram(vals, bins=numpy.arange(mx + 1))[0]
        expected = numpy.array([float(trial) / mx] * mx)
        if not hypothesis_testing.chi_square_test(counts, expected):
            self.fail()
