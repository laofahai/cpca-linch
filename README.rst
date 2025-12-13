cpca-linch
==========

A Python module for extracting Chinese province, city, and district information from address strings.

Fork from `DQinYuan/chinese_province_city_area_mapper <https://github.com/DQinYuan/chinese_province_city_area_mapper>`_ with updated 2025 administrative division data.

Installation
------------

.. code-block:: bash

    pip install cpca-linch

Usage
-----

.. code-block:: python

    import cpca

    df = cpca.transform(["徐汇区虹漕路461号58号楼5楼", "广东省中山市沙溪镇云汉轻纺城"])
    print(df)

Output::

         省    市    区              地址
    0  上海市  上海市  徐汇区  虹漕路461号58号楼5楼
    1  广东省  中山市  沙溪镇       云汉轻纺城

Key Improvements
----------------

1. Updated administrative division data to 2025 (from `xiangyuecn/AreaCity-JsSpider-StatsGov <https://github.com/xiangyuecn/AreaCity-JsSpider-StatsGov>`_)
2. Support for towns in prefecture-level cities without districts (Dongguan, Zhongshan, Danzhou, Jiayuguan)
3. Removed latitude/longitude data for smaller package size

Full documentation: `https://github.com/laofahai/cpca-linch <https://github.com/laofahai/cpca-linch>`_

License
-------

MIT
