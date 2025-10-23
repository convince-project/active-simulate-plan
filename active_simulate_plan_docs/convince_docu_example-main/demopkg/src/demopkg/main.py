#!/usr/bin/env python3
# Copyright (c) 2024 - for information on the respective copyright owner
# see the NOTICE file

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the main.

Call it with

.. code-block:: bash
    
        python -m demopkg
"""

import sys
from typing import Optional, Sequence

import argparse

def main(args: Optional[Sequence[str]] = None) -> int:
    """
    Entry point for the application.
    """
    argparse.ArgumentParser(description='Demo package')
    print("Hello World!")
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
