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

7. Added 10 reviewed address aliases and historical guidance for Dachang and Meilie districts in 0.5.1; ambiguous default mappings disclose candidate cities.
8. Fixed province-constrained city/district aliases, separated reverse-order addresses, Luqiao district road filtering, and province-abbreviation positions in 0.5.2.

Output validation
-----------------

By default, output combinations are checked against the bundled current and historical tables, loaded locally without a network request per address. Alias disambiguation also uses parent relationships. Conflicting explicit names are retained and marked ``待核验``; historical names keep their original spelling and status. A match only confirms membership in this snapshot, not the real-world validity of the input address.

``include_status=False`` disables output status checking and its columns; parsing still applies parent constraints. Both parsing modes share these rules. Neither mode guarantees higher accuracy for every input.

Full documentation: `https://github.com/laofahai/cpca-linch <https://github.com/laofahai/cpca-linch>`_

License
-------

MIT
