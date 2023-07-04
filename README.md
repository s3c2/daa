<h1 align="center">
Differential Alert Analysis
</h1>
<p align="center">
<!-- <a target="_blank" href="https://search.maven.org/artifact/com.webencyclop.core/mftool-java"><img src="https://img.shields.io/maven-central/v/com.webencyclop.core/mftool-java.svg?label=Maven%20Central"/></a> 
<a target="_blank" href="https://www.codacy.com/gh/ankitwasankar/mftool-java/dashboard?utm_source=github.com&utm_medium=referral&utm_content=ankitwasankar/mftool-java&utm_campaign=Badge_Coverage"><img src="https://app.codacy.com/project/badge/Coverage/0054db87ea0f426599c3a30b39291388" /></a> -->
<!-- <a href="https://www.codacy.com/gh/ankitwasankar/mftool-java/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ankitwasankar/mftool-java&amp;utm_campaign=Badge_Grade"><img src="https://badge.fury.io/py/pyplay.svg"/></a>
<a target="_blank" href="./license.md"><img src="https://camo.githubusercontent.com/8298ac0a88a52618cd97ba4cba6f34f63dd224a22031f283b0fec41a892c82cf/68747470733a2f2f696d672e736869656c64732e696f2f707970692f6c2f73656c656e69756d2d776972652e737667" /></a> -->
<!-- &nbsp <a target="_blank" href="https://www.linkedin.com/in/myles-dunlap/"><img height="20" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a> -->
</p>


<p align="center">
  This repository contains the <strong>Differential Alert Analysis (DAA)</strong> source code.
  DAA is a Python library developed to find fixed vulnerabilities using the output of SAST tools.
</p>

<p align="center">
<a href="#introduction">Introduction</a> &nbsp;&bull;&nbsp;
<a href="#installation">Installation</a> &nbsp;&bull;&nbsp;
<!-- <a href="#usage">Usage</a> &nbsp;&bull;&nbsp; -->
<a href="#license">License</a> &nbsp;&bull;&nbsp;
<!-- <a href="#contact">Contact</a> -->
</p>

# Introduction
DAA is a language-agnostic algorithm that
uses the outputs of lightweight and imprecise off-the-shelf
static analysis security tools (SAST) to discover resolved
vulnerabilities in software projects without relying on
an announcement. The key insight driving DAA is that
when a fix is introduced, it will eliminate a SAST alert
present in the prior version.

# Installation
Clone the DAA repository and pip install from the clone. We recommend creating a [virtual environment](https://docs.python.org/3/library/venv.html) to install DAA. 

```shell
git clone git@github.com:s3c2/daa.git
cd daa

python3 -m venv .venv
source .venv/bin/activate
pip3 install .
```

# Use DAA as a library:
```python
from daa import daa_hierarchy
import pandas as pd

if __name__ == '__main__':
    
    # SET the alerts generated from your SAST tool
    previous_alerts = pd.read_csv("PATH_TO_PREVIOUS_ALERTS.csv")
    current_alerts = pd.read_csv("PATH_TO_CURRENT_ALERTS.csv")
    
    # Run DAA on the alerts
    daa_results = daa_hierarchy.DAA(previous_alerts, current_alerts)
```

# License
DAA is available under the Apache-2.0 License

  * ***Apache-2.0 License***: See [LICENSE](./LICENSE) file for details.

