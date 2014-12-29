from __future__ import division, print_function

from itertools import chain, imap
from operator import methodcaller

"""
DefaultNamespace is injected instead of Namespace from argparse

Really nice to programatically use a python CLI script without Popen or similar.
The only requirement is that the main method for the script takes an argparse.Namespace as argument, this is not that uncommon.

Example
-------

    d = DefaultNamespace(required=['hosts'], default={'cassandra-bin-dir', '/usr/bin'}, const={'new_password', True})
    args = d(hosts=['cas4.watty.io', ], table='test')  #use it as a argparse.Namespace


NOTE
----
s3-bucket-name is saved and accesed by s3_bucket_name

"""


concat_dicts = lambda *dicts: dict(
    chain.from_iterable(
        imap(
            methodcaller('iteritems'),
            dicts
        )
    )
)


select_dict = lambda d, selects: dict(
    imap(
        lambda select: (select, d[select]),
        selects,
    )
)


replace = methodcaller('replace', '-', '_')
replace_keys = lambda d: dict(zip(*(
    map(replace, d.keys()),
    d.values()
)))


class Namespace(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, name):
        return self.kwargs[name] if name in self.kwargs else None

    def __repr__(self):
        return "{}(\n{})".format(
            self.__class__.__name__,
            "".join(
                imap(
                    lambda (key, value): "    {key}={value},\n".format(
                        key=key,
                        value=value,
                    ),
                    self.kwargs.iteritems()
                )
            )
        )

    def __str__(self):
        return self.__repr__()


class DefaultNamespace(object):
    """
    default values are setting if none is present in __call__
    const values overwrites whutever value given in kwargs for __call__
    note that the default value for const is always None
    """
    def __init__(self, required=[], default={}, const={}):
        self.required = map(replace, required)
        self.default = replace_keys(default)
        self.const = replace_keys(const)

    def __repr__(self):
        return "{}(\n{})".format(
            self.__class__.__name__,
            "".join([
                "    required={},\n".format(self.required),
                "    default={},\n".format(self.default),
                "    const={},\n".format(self.const),
            ])
        )

    def __str__(self):
        return self.__repr__()

    def __call__(self, **kwargs):
        assert(set(self.required) <= set(kwargs))

        consted_keys = set(self.const) & set(kwargs)
        consted = select_dict(self.const, consted_keys)

        defaulted_keys = set(self.default) - set(kwargs)
        defaulted = select_dict(self.default, defaulted_keys)

        valued_keys = set(kwargs) - set(self.const)
        valued = select_dict(kwargs, valued_keys)

        assert(not(
            set(valued) & set(consted) & set(defaulted)
        ))

        return Namespace(
            **concat_dicts(
                valued,
                consted,
                defaulted,
            )
        )
