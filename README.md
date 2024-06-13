
<div align="center" style="margin-top: 2rem;">
  <img src="https://gloe.ideos.com.br/_static/assets/gloe-logo.png"><br>
</div>



| | | 
| ---:|----|
| Testing | [![CI - Test](https://github.com/ideos/gloe/actions/workflows/test.yml/badge.svg)](https://github.com/ideos/gloe/actions/workflows/test.yml) [![Coverage](https://codecov.io/github/ideos/gloe/coverage.svg?branch=main)](https://codecov.io/gh/ideos/gloe) |
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe) [![Anaconda Latest Release](https://anaconda.org/conda-forge/gloe/badges/version.svg)](https://anaconda.org/conda-forge/gloe) [![Supported Python versions](https://img.shields.io/pypi/pyversions/gloe.svg?color=%2334D058)](https://pypi.org/project/gloe) |
| Meta | [![License - Apache 2.0](https://img.shields.io/pypi/l/gloe.svg?color=%2304b367)](https://github.com/ideos/gloe/blob/main/LICENSE) |
| Code | [![Code quality](https://github.com/ideos/gloe/actions/workflows/code-quality.yml/badge.svg)](https://github.com/ideos/gloe/actions/workflows/code-quality.yml) [![Style](https://img.shields.io/badge/style-black-000000.svg)](https://github.com/psf/black) [![Flake8](https://img.shields.io/badge/flake8-checked-7854cc)](https://flake8.pycqa.org/) [![Mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://www.mypy-lang.org/)|

***

**Read the documentation**: [gloe.ideos.com.br](https://gloe.ideos.com.br)

**Souce code**: [github.com/ideos/gloe](https://github.com/ideos/gloe)

**FAQ**: [gloe.ideos.com.br/faq.html](https://gloe.ideos.com.br/faq.html)

***

# Write a Better Python Flow

Gloe (pronounced /ɡloʊ/, like "glow") is a general-purpose library made to help developers create, maintain, document, and test both operational and flow-oriented code. It is particularly useful in data science and machine learning pipelines, as well as in servers and scripts, or any area where there is a gap between the code and the logical business understanding. Gloe is not intended to be used across an entire application or to replace existing libraries. Instead, it is built to integrate with other tools and to address areas where the code complexity may be higher than expected.

## Key Features

- Use pure Python to write **type-safe** pipelines.
- Express a pipeline as a set of **atomic**, **isolated**, **extensible** and **trackable** units of responsibility called [transformers](https://gloe.ideos.com.br/theory.html).
- [Validate the input, the output and the changes between input and output](https://gloe.ideos.com.br/getting-started/ensurers.html) of transformers during execution.
- [Mix sync and async](https://gloe.ideos.com.br/getting-started/async-transformers.html#async-pipelines) code without worrying about its concurrent nature.
- Write a **readable** and **maintainable** code for extremely **complex flows**. ¹ 
- Use it where and when you need it. Gloe does not require any significant changes to your existing workflow.
- [Visualize you pipelines](https://gloe.ideos.com.br/getting-started/plotting.html) and the data flowing through it. ²
- Use a functional approach to work with [conditions](https://gloe.ideos.com.br/getting-started/conditional-flows.html) and [collections](https://gloe.ideos.com.br/api-reference/gloe.collection.html).

<sub>1. Gloe emerged in the context of a large application with extremely complex business logic. After transitioning the code to Gloe, maintenance efficiency improved by 200%, leading the entire team to adopt it widely.</sub>

<sub style="display: block; margin-top: -0.5rem;">2. This feature is under development.</sub>

## Installing

```shell
# PyPI
pip install gloe
```


```shell
# or conda
conda install -c conda-forge gloe
```

## Example

Consider the following pipeline. Its purpose is to send two types of promotional emails to users with specific roles. First, it extracts a role from an HTTP request, then fetches the users who belong to this role, sends the corresponding email to each group of users, and finally logs the results of the emails sent.


```python
send_promotion = (
    extract_request_role >>
    get_users >> (
        filter_basic_subscription >> send_basic_subscription_promotion_email,
        filter_premium_subscription >> send_premium_subscription_promotion_email,
    ) >>
    log_emails_result
)
```
By reading the code, do you think is it clear enough?

Each step of a Gloe pipeline is called a transformer and creating one is as easy as:

```python
from gloe import transformer

@transformer
def extract_request_role(req: Request) -> str:
    # your logic goes here
```

You can connect many transformers using the right shift operator, just like the above example. When the argument of the `>>` is a tuple, you are creating branches. 

> Learn more about [creating transformers](https://gloe.ideos.com.br/getting-started/transformers.html) and [pipelines](https://gloe.ideos.com.br/getting-started/transformers.html#building-a-pipeline).

### Maintainance

When the manager asks you to include promotional emails for unsubscribed users as well, the refactoring process is straightforward:

```python
send_promotion = (
    extract_request_role >>
    get_users >> (
        filter_basic_subscription >> send_basic_subscription_promotion_email,
        filter_premium_subscription >> send_premium_subscription_promotion_email,
        filter_unsubscribed >> send_unsubscribed_promotion_email,
    ) >>
    log_emails_result
)
```

> See the [full code](https://gloe.ideos.com.br/getting-started/plotting.html) (transformers definition).

### Type checking

If, by some chance, you connect two transformers with incompatible types, the IDE along with [Mypy](https://github.com/python/mypy) will warn you about the malformed pipeline.

For example, suppose you implemented the `send_unsubscribed_promotion_email` transformer expecting a list of integer ids:

```python
@transformer
def send_unsubscribed_promotion_email(ids: list[int]) -> Result:
    ...
```

But the `filter_unsubscribed` transformer returns a list of users:

```python
@transformer
def filter_unsubscribed(users: list[User]) -> list[User]:
    ...
```

The result will be something like this:

![Malformed pipeline example](https://gloe.ideos.com.br/_images/malformed-pipeline-example.jpeg)

### Simple Usage

Considering is everything okay about the types, this pipeline can be invoked from a server, for example:

```python
@users_router.post('/send-promotion/:role')
def send_promotion_emails_route(req: Request):
    return send_promotion(req)
```
### Quick Documentation

When you need to document it somewhere, you can just [plot it](https://gloe.ideos.com.br/getting-started/plotting.html).

![Graph for send_promotion](https://gloe.ideos.com.br/_images/graph_example.jpeg)

### Integration 

Suppose you don't need to extract the role within the pipeline because you are using a web framework that already does it, like [FastAPI](https://fastapi.tiangolo.com/), you can remove the `extract_request_role` transformer. Since the incoming type for `get_users` is string, the configuration would be:


```python
send_promotion = (
    get_users >> (
        filter_basic_subscription >> send_basic_subscription_promotion_email,
        filter_premium_subscription >> send_premium_subscription_promotion_email,
        filter_unsubscribed >> send_unsubscribed_promotion_email,
    ) >>
    log_emails_result
)


@users_router.post('/send-promotion/{role}')
def send_promotion_emails_route(role: str):
    return send_promotion(role)
```

We hope the above example illustrates how easily you can identify maintenance points and gain confidence that the rest of the code will continue to working properly, as long as the transformers' interfaces remain satisfied.


## Motivation

Software development has lots of patterns and good practices related to the code itself, like how to document, test, structure and what programming paradigm to use. However, beyond all that, we believe that the key point of a successful software project is a good communication between everyone involved in the development. Of course, this communication is not necessarily restricted to meetings or text messages, it is present also in documentation artifacts and in a well-written code.

When developers write a code, they are telling a story to the next person who will read or/and refactor it. Depending on the code's quality, this story could be quite confusing, with no clear roles of the characters and a messy plot (sometimes with an undesired twist). The next person to maintain the software may take a long time to clearly understand the narrative and make it clear, or they will simply give up, leaving it as is.


### How Can Gloe Help Me?

Gloe comes to turn this story coherent, logically organized and easy to follow. This is achieved by dividing the code into [concise steps](https://gloe.ideos.com.br/theory.html) with an unambiguous responsibility and explicit interface. Then, Gloe allows you to connect these steps, clarifying their collaboration and identifying necessary changes during refactoring. Thus, you can quickly understand the entire story being told and enhance it. Inspired by things like [natural transformation](https://ncatlab.org/nlab/show/natural+transformation) and Free Monad (present in [Scala](https://typelevel.org/cats/datatypes/freemonad.html) and [Haskell](https://serokell.io/blog/introduction-to-free-monads)), Gloe implemented this approach using functional programming and strong typing concepts.

### Gloe is not a workflow orchestrator

Currently, unlike platforms like [Air Flow](https://airflow.apache.org/) that include scheduler backends for task orchestration, Gloe's primary purpose is to aid in development. The [graph structure](https://gloe.ideos.com.br/theory.html) aims to make the code [more flat and hence readable](https://en.wikibooks.org/wiki/Computer_Programming/Coding_Style/Minimize_nesting). However, it is important to note that Gloe does not offer functionalities for executing tasks in a dedicated environment, nor does it directly contribute to execution speed or scalability improvements.


## License

[Apache License Version 2.0](https://github.com/ideos/gloe/blob/main/LICENSE)