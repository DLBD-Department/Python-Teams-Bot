#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

""" Bot Configuration """


load_dotenv()

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    
    # Inter-change between these two ↓: 1. if using emulator, or 2. Azure-registered Bot resource

#    APP_ID = os.environ.get("MicrosoftAppId", "")
#    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    APP_ID = os.environ.get("MicrosoftAppId", os.getenv('APP_ID'))
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", os.getenv('APP_PASSWORD'))
