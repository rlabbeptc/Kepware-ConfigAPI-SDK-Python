# -------------------------------------------------------------------------
# Copyright (c) PTC Inc. and/or all its affiliates. All rights reserved.
# See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# r"""

# **Kepware Configuration (kepconfig) API Library**
# --

# This is a package to help create Python applications to conduct operations with the Kepware Configuration API. 
# This package is designed to work with all versions of Kepware that support the Configuration API including 
# Thingworx Kepware Server (TKS), Thingworx Kepware Edge (TKE) and KEPServerEX (KEP).

# Copyright (c) PTC Inc. and/or all its affiliates. All rights reserved.
# See License.txt in the project root for
# license information.

# """

"""
.. include:: ../README.md
"""
__version__ = "1.2.0"
from . import connection, error
from .utils import path_split

