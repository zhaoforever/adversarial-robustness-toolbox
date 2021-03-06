from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import numpy as np

from art.utils import load_mnist, projection, random_sphere, to_categorical
from art.utils import random_targets, get_label_conf, get_labels_np_array, preprocess


BATCH_SIZE = 10
NB_TRAIN = 100
NB_TEST = 100


class TestUtils(unittest.TestCase):
    def test_projection(self):
        # Get MNIST
        (x, _), (_, _), _, _ = load_mnist()
        # Probably don't need to test everything
        x = x[:100]
        t = tuple(range(1, len(x.shape)))
        rand_sign = 1 - 2 * np.random.randint(0, 2, size=x.shape)
        
        x_proj = projection(rand_sign*x, 3.14159, 1)
        self.assertEqual(x.shape, x_proj.shape)
        self.assertTrue(np.allclose(np.sum(np.abs(x_proj), axis=t), 3.14159, atol=10e-8))
        
        x_proj = projection(rand_sign*x, 3.14159, 2)
        self.assertEqual(x.shape, x_proj.shape)
        self.assertTrue(np.allclose(np.sqrt(np.sum(x_proj**2, axis=t)), 3.14159, atol=10e-8))
        
        x_proj = projection(rand_sign*x, 0.314159, np.inf)
        self.assertEqual(x.shape, x_proj.shape)
        self.assertEqual(x_proj.min(), -0.314159)
        self.assertEqual(x_proj.max(), 0.314159)
        
        x_proj = projection(rand_sign*x, 3.14159, np.inf)
        self.assertEqual(x.shape, x_proj.shape)
        self.assertEqual(x_proj.min(), -1.0)
        self.assertEqual(x_proj.max(), 1.0)

    def test_random_sphere(self):
        x = random_sphere(10, 10, 1, 1)
        self.assertEqual(x.shape, (10, 10))
        self.assertTrue(np.all(np.sum(np.abs(x), axis=1) <= 1.0))
        
        x = random_sphere(10, 10, 1, 2)
        self.assertTrue(np.all(np.linalg.norm(x, axis=1) < 1.0))
        
        x = random_sphere(10, 10, 1, np.inf)
        self.assertTrue(np.all(np.abs(x) < 1.0))
    
    def test_to_categorical(self):
        y = np.array([3, 1, 4, 1, 5, 9])
        y_ = to_categorical(y)
        self.assertEqual(y_.shape, (6, 10))
        self.assertTrue(np.all(y_.argmax(axis=1) == y))
        self.assertTrue(np.all(np.logical_or(y_ == 0.0, y_ == 1.0)))
        
        y_ = to_categorical(y, 20)
        self.assertEqual(y_.shape, (6, 20))
        
    def test_random_targets(self):
        y = np.array([3, 1, 4, 1, 5, 9])
        y_ = to_categorical(y)
        
        random_y = random_targets(y, 10)
        self.assertTrue(np.all(y != random_y.argmax(axis=1)))
        
        random_y = random_targets(y_, 10)
        self.assertTrue(np.all(y != random_y.argmax(axis=1)))
    
    def test_get_label_conf(self):
        y = np.array([3, 1, 4, 1, 5, 9])
        y_ = to_categorical(y)
        
        logits = np.random.normal(10 * y_, scale=0.1)
        ps = (np.exp(logits).T / np.sum(np.exp(logits), axis=1)).T
        c, l = get_label_conf(ps)
        
        self.assertEqual(c.shape, y.shape)
        self.assertEqual(l.shape, y.shape)
        
        self.assertTrue(np.all(l == y)) 
        self.assertTrue(np.allclose(c, 0.99, atol=1e-2))
        
    def test_get_labels_np_array(self):
        y = np.array([3, 1, 4, 1, 5, 9])
        y_ = to_categorical(y)
        
        logits = np.random.normal(1 * y_, scale=0.1)
        ps = (np.exp(logits).T / np.sum(np.exp(logits), axis=1)).T
        
        labels = get_labels_np_array(ps)
        self.assertEqual(labels.shape, y_.shape)
        self.assertTrue(np.all(labels == y_))
        
    def test_preprocess(self):
        # Get MNIST
        (x, y), (_, _), _, _ = load_mnist()
        
        x = (255 * x).astype('int')[:100]
        y = np.argmax(y, axis=1)[:100]
        
        x_, y_ = preprocess(x, y)
        self.assertEqual(x_.shape, x.shape)
        self.assertEqual(y_.shape, (y.shape[0], 10))
        self.assertEqual(x_.max(), 1.0)
        self.assertEqual(x_.min(), 0)
        
        (x, y), (_, _), _, _ = load_mnist()
        
        x = (5 * x).astype('int')[:100]
        y = np.argmax(y, axis=1)[:100]
        x_, y_ = preprocess(x, y, nb_classes=20, max_value=5)
        self.assertEqual(x_.shape, x.shape)
        self.assertEqual(y_.shape, (y.shape[0], 20))
        self.assertEqual(x_.max(), 1.0)
        self.assertEqual(x_.min(), 0)


if __name__ == '__main__':
    unittest.main()
