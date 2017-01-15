"""Ops for tensor initialization"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import numpy as np
import tensorflow as tf
from deepchem.nn.model_ops import variable
from deepchem.nn.model_ops import random_uniform_variable
from deepchem.nn.model_ops import random_normal_variable
from deepchem.nn.activations import get_from_module

def get_fans(shape, dim_ordering='th'):
  if len(shape) == 2:
    fan_in = shape[0]
    fan_out = shape[1]
  elif len(shape) == 4 or len(shape) == 5:
    # Assuming convolution kernels (2D or 3D).
    # TH kernel shape: (depth, input_depth, ...)
    # TF kernel shape: (..., input_depth, depth)
    if dim_ordering == 'th':
      receptive_field_size = np.prod(shape[2:])
      fan_in = shape[1] * receptive_field_size
      fan_out = shape[0] * receptive_field_size
    elif dim_ordering == 'tf':
      receptive_field_size = np.prod(shape[:2])
      fan_in = shape[-2] * receptive_field_size
      fan_out = shape[-1] * receptive_field_size
    else:
      raise ValueError('Invalid dim_ordering: ' + dim_ordering)
  else:
    # No specific assumptions.
    fan_in = np.sqrt(np.prod(shape))
    fan_out = np.sqrt(np.prod(shape))
  return fan_in, fan_out


def uniform(shape, scale=0.05, name=None):
  return random_uniform_variable(shape, -scale, scale, name=name)


def normal(shape, scale=0.05, name=None):
  return random_normal_variable(shape, 0.0, scale, name=name)


def lecun_uniform(shape, name=None, dim_ordering='th'):
  """LeCun uniform variance scaling initializer.

  # References
      LeCun 98, Efficient Backprop,
      http://yann.lecun.com/exdb/publis/pdf/lecun-98b.pdf
  """
  fan_in, fan_out = get_fans(shape, dim_ordering=dim_ordering)
  scale = np.sqrt(3. / fan_in)
  return uniform(shape, scale, name=name)


def glorot_normal(shape, name=None, dim_ordering='th'):
  """Glorot normal variance scaling initializer.

  # References
      Glorot & Bengio, AISTATS 2010
  """
  fan_in, fan_out = get_fans(shape, dim_ordering=dim_ordering)
  s = np.sqrt(2. / (fan_in + fan_out))
  return normal(shape, s, name=name)


def glorot_uniform(shape, name=None, dim_ordering='th'):
  fan_in, fan_out = get_fans(shape, dim_ordering=dim_ordering)
  s = np.sqrt(6. / (fan_in + fan_out))
  return uniform(shape, s, name=name)


def he_normal(shape, name=None, dim_ordering='th'):
  """He normal variance scaling initializer.

  # References
      He et al., http://arxiv.org/abs/1502.01852
  """
  fan_in, fan_out = get_fans(shape, dim_ordering=dim_ordering)
  s = np.sqrt(2. / fan_in)
  return normal(shape, s, name=name)


def he_uniform(shape, name=None, dim_ordering='th'):
  """He uniform variance scaling initializer.
  """
  fan_in, fan_out = get_fans(shape, dim_ordering=dim_ordering)
  s = np.sqrt(6. / fan_in)
  return uniform(shape, s, name=name)


def orthogonal(shape, scale=1.1, name=None):
  """Orthogonal initializer.

  # References
      Saxe et al., http://arxiv.org/abs/1312.6120
  """
  flat_shape = (shape[0], np.prod(shape[1:]))
  a = np.random.normal(0.0, 1.0, flat_shape)
  u, _, v = np.linalg.svd(a, full_matrices=False)
  # Pick the one with the correct shape.
  q = u if u.shape == flat_shape else v
  q = q.reshape(shape)
  return variable(scale * q[:shape[0], :shape[1]], name=name)


def identity(shape, scale=1, name=None):
  if len(shape) != 2 or shape[0] != shape[1]:
    raise ValueError('Identity matrix initialization can only be used '
                     'for 2D square matrices.')
  else:
    return variable(scale * np.identity(shape[0]), name=name)


def zero(shape, name=None):
  return tf.zeros(shape, name=name)


def one(shape, name=None):
  return tf.ones(shape, name=name)


def get(identifier, **kwargs):
  return get_from_module(identifier, globals(),
                         'initialization', kwargs=kwargs)
