# Reference Library

本目录是论文、数据集和外部代码来源的统一入口。目标是在方法实现之前记录
来源、版本和用途，避免完成实验后再反向寻找 reference。它保持轻量，不替代
Zotero 等个人文献工具，也不建立独立数据库。

## 文件

- [`catalog.csv`](catalog.csv)：所有候选、已审阅和已采用来源的主索引。
- [`bibliography.bib`](bibliography.bib)：可直接供论文使用的 BibTeX。
- [`notes/NOTE_TEMPLATE.md`](notes/NOTE_TEMPLATE.md)：需要详细阅读时使用的简短模板。
- [`user_materials/`](user_materials/README.md)：Tianhang 自行放入的论文、PDF、
  讲义或其他材料；默认不进入 Git。

外部 GitHub 仓库不要复制进本目录。需要源码检查时，将 checkout 放入已忽略的
`external/`，并在 `catalog.csv` 中记录 repository URL、exact commit 和相关
review/task。

## 最小工作方式

1. 在采用算法、代码或数据处理方法前，先在 `catalog.csv` 登记来源。
2. Paper 固定 DOI、arXiv version 或正式出版信息；代码固定 tag 或 commit。
3. 初步浏览标为 `screened`，完成与当前问题相关的核查后标为 `reviewed`。
4. 真正用于项目方法时，在 `project_use` 和 `linked_record` 中说明用途，并在
   对应 task/review 中标明 `Inherited`、`Adapted`、`Project-designed` 或
   `Implementation-only`。
5. 需要写入论文的来源加入 `bibliography.bib`。引用前复核作者、标题、年份和
   publication venue。

允许的 `review_status` 是：

- `registered`：只登记，尚未阅读；
- `screened`：已检查与项目的表面相关性；
- `reviewed`：已核查与当前使用有关的具体内容；
- `adopted`：已由 Tianhang 明确采用；
- `rejected`：评估后不采用，但保留原因和来源。

收录不等于采用，未找到相同方法也不等于创新。项目自己的选择仍应称为
`Project-designed`，直到充分 literature review 和 Tianhang 明确确认其贡献
表述。
