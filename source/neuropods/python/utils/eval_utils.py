#
# Uber, Inc. (c) 2018
#

import logging
import numpy as np
from testpath.tempdir import TemporaryDirectory

from neuropods.loader import load_neuropod
from neuropods.utils.env_utils import create_virtualenv, eval_in_virtualenv

logger = logging.getLogger(__name__)


def check_output_matches_expected(out, expected_out):
    for key, value in expected_out.items():
        if value.dtype.type == np.string_:
            # All strings are equal
            success_condition = (value == out[key]).all()
        else:
            # All the values are close
            success_condition = np.allclose(value, out[key])

        if not success_condition:
            raise ValueError("{} does not match expected value!".format(key))


def print_output_summary(out):
    logger.info("No expected test output specified; printing summary to stdout")
    for key, value in out.items():
        if isinstance(value, np.ndarray):
            logger.info("\t{}: np.array with shape {} and dtype {}".format(key, value.shape, value.dtype))
        else:
            raise ValueError("All outputs must be numpy arrays! Output `{}` was of type `{}`".format(key, type(value)))


def eval_in_process(neuropod_path, test_input_data):
    """
    Used to run evaluation without a virtualenv
    """
    with load_neuropod(neuropod_path) as model:
        # Run inference and return the output
        return model.infer(test_input_data)


def load_and_test_neuropod(neuropod_path, test_input_data, test_expected_out=None,
                           use_virtualenv=False, test_deps=[], test_virtualenv=None):
    """
    Loads a neuropod in a virtualenv and verifies that inference runs.
    If expected output is specified, the output of the model is checked against
    the expected values.

    Raises a ValueError if the outputs don't match the expected values
    """

    if use_virtualenv:
        # Run the model in a virtualenv
        if test_virtualenv is None:
            # Create a temporary virtualenv if one is not specified
            with TemporaryDirectory() as virtualenv_dir:
                create_virtualenv(virtualenv_dir, packages_to_install=test_deps)
                out = eval_in_virtualenv(neuropod_path, test_input_data, virtualenv_dir)
        else:
            # Otherwise run in the specified virtualenv
            out = eval_in_virtualenv(neuropod_path, test_input_data, test_virtualenv)
    else:
        # Run the evaluation in the current process
        out = eval_in_process(neuropod_path, test_input_data)

    # Check the output
    if test_expected_out is not None:
        # Throws a ValueError if the output doesn't match the expected value
        check_output_matches_expected(out, test_expected_out)
    else:
        # We don't have any expected output so print a summary
        print_output_summary(out)
