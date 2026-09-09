cpca-linch
==========

A Python module for extracting Chinese province, city, and district information from address strings.

Fork from `DQinYuan/chinese_province_city_area_mapper <https://github.com/DQinYuan/chinese_province_city_area_mapper>`_ with a 2026-04-03 data snapshot and official supplements reviewed on 2026-09-08.

Installation
------------

.. code-block:: bash

    pip install cpca-linch

Usage
-----

.. code-block:: python

    import cpca

    df = cpca.transform(["徐汇区虹漕路461号58号楼5楼", "广东省中山市沙溪镇云汉轻纺城"], include_status=False)
    print(df)

Output::

         省    市    区              地址
    0  上海市  上海市  徐汇区  虹漕路461号58号楼5楼
    1  广东省  中山市  沙溪镇       云汉轻纺城

Key Improvements
----------------

1. Updated administrative division data to upstream version 2025.251231.260403 (collected 2026-04-03), with official supplements for He'an, Hekang and Cenling counties. This is not a guarantee of exhaustive nationwide coverage as of the review date.
2. Support for towns in prefecture-level cities without districts (Dongguan, Zhongshan, Danzhou, Jiayuguan)
3. Removed latitude/longitude data for smaller package size
4. Kept historical names in a separate compatibility table; old addresses return their original names, without automatic conversion to current divisions
5. Loaded division names into a private jieba tokenizer to recognize newly established divisions
6. Added recognition status, explanations and current-name suggestions by default. Use ``include_status=False`` to preserve the original output columns. Historical names are retained rather than silently rewritten; farm/park names are labelled as places.

Full documentation: `https://github.com/laofahai/cpca-linch <https://github.com/laofahai/cpca-linch>`_

License
-------

MIT
