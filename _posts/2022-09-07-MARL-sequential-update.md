---
title: MARL之sequential update
intro: 小组会内容，特此记录。主要讲述四篇相关文献的发展脉络。
author: Sapio-S
date: 2022-09-07
categories: [科研, paper]
tags: [RL,笔记,技术,论文]
math: true
---



## 合作的MARL

### 问题描述

多机的POMDP（Partially Observable Markov Decision Process）可以用$<N, S, A, P, r, \gamma>$ 描述。其中，$N$是智能体个数，$S$是智能体的联合状态State，$A$是智能体的联合行为Action，$P$是状态转移函数Transition Probability function，$r$是多机共享的joint reward function，$\gamma$是折扣因子discount factor。

联合策略joint policy由各个agent的独立策略组成，

我们需要找到一个最优的policy从而maximize the expected total reward:

### 常见处理方式

同单机一样，多机RL也可以大致分为value-based和policy-based两种。

#### Value Decomposition

这一派算法的思路是把global Q function拆分为多个local Q functions，【图片：/2022-09-05-10-57-56-image.png" title="" alt="" width="386">，让每个agent学习自己的Q function。决策时，每个agent选择让自己的local Q最大的动作，就可以使得整体最优。显然，不是任意一种拆分方式（$f_{mix}$）都可以满足要求。我们需要拆分方式满足Individual Global Max（IGM）。

即：

【图片：/2022-09-05-10-52-41-image.png" alt="" width="333">

显然，Value Decomposition需要对global Q function的拆分方式进行特殊设计，使得它满足上述的IGM条件。常见的local Q function构造包括：

- VDN（Additivity，简单加和）【图片：/2022-09-05-10-53-22-image.png" title="" alt="" width="173">

- QMIX（Monotonicity，单调性条件）【图片：/2022-09-05-10-55-10-image.png" title="" alt="" width="100">

注意，这些拆分方式与IGM是不等价的。它们都是IGM的充分不必要条件，限制条件更为严格。

#### Policy Gradient

这一类方法直接通过梯度下降对策略进行优化。MAPPO就是这一类的典型算法。

### 常用术语

#### parameter sharing

如果每个agent学习自己单独的Q函数/策略，那么参数大小将随着agent的数量相应成倍增加（十个agent就有十个不同的网络需要训练！）。为了减少参数，同时增加训练的速度和稳定性，Value Decomposition和Policy Gradient都使用了parameter sharing的技巧，让各个agent共享相同的参数。

#### CTDE

Centralized框架把所有智能体联合建模来学习一个联合的策略，该策略的输入是所有智能体的联合观测，输出所有智能体的联合动作。但是中心化训练框架的问题在于输入和输出空间巨大，难以适应较大规模的多智能体系统。

Decentralized结构中，每个智能体的训练独立于其他智能体，其策略网络根据局部观测输出要采取的动作。去中心化的训练框架会面临环境不平稳的问题，这是因为在训练过程中，某一智能体将其他智能体看成环境的一部分，然而其他智能体的训练将导致环境中的状态转移函数发生变化，从而破坏强化学习算法遵循的马尔可夫假设。

Centralized Training and Decentralized Execution (CTDE)是当前MARL非常常见的运算模式。在训练时采用中心化的模式，而在训练结束之后智能体仅仅根据自身的局部观测，利用训练好的策略网络进行决策。从而在一定程度上同时克服环境不平稳和大规模智能体的问题。在training阶段，各个agent可以获取到global信息，从而选择全局最优的策略；在inference阶段，各个agent只能根据自己的观测选择动作。

【图片：/2022-09-05-14-20-24-image.png" title="" alt="" width="379">

【图片：/2022-09-05-14-21-07-image.png" title="" alt="" width="368">

在MAPPO里，CTDE体现在Actor-Critic的结构里。Actor仅通过agent的local observation选择动作，而critic则会通过整体的global observation（或者多agent local observation concat出来的信息）评判动作的好坏。training阶段，actor & critic都会不断迭代，但是在inference阶段，agent仅通过actor进行决策，不需要全局观测的指导。

## sequential / auto-regressive update

### 从简单的例子看share policy

但是，上述的share policy/share parameter存在着一些问题：

- 要求agent必须同质化（拥有相同的action space & observation space）；

- 不能保证收敛到全局最优。

针对第二点，我们考虑2-agent的XOR问题：两个agent必须一个选择1一个选择0才可以得分，否则不得分。在这个情境中，value decomposition无法得到满足IGM的Q function拆分方式；share parameter的policy gradient也无法获得最优解。而不进行parameter sharing的policy gradient则可以取得最优解。

扩展至n-agent的XOR问题，不难求出，share policy的optimal joint return ($J^*_{share}$) 与individual policy的optimal joint return ($J^*$)满足下式：

【图片：/2022-09-05-13-52-53-image.png" alt="" width="87">

### 单调性问题

但是，仅仅取消parameter sharing也不能保证使用policy gradient的joint policy可以收敛到全局最优解，因为我们很难保证每一步更新都是单调的。

考虑2-agent XOR的升级问题：$r(a_1,a_2)=a_1*a_2$，且初始点位于第四象限。如果agent根据各自策略决策，它们将倾向于将点向左上方优化，这很有可能会让reward进一步降低。而一个更为合理的更新方式则应该让点落入第一象限，取得更大值。

【图片：/2022-09-05-13-46-08-image.png" alt="" width="355">

### sequential / auto-regressive方式

有没有办法可以解决上述的问题呢？

考虑agent不再同时选择行动，而是遵从一定的顺序先后进行决策。换言之，假如之前智能体的joint policy是【图片：/2022-09-05-14-35-12-image.png" title="" alt="" width="164">，那么现在就变为【图片：/2022-09-05-14-35-36-image.png" title="" alt="" width="210">。

此时，我们可以这样定义优势函数：

【图片：/2022-09-05-15-58-16-image.png" title="" alt="" width="575">

这意味着h到m这几个agent采取的动作对整体价值的影响。

根据Multi-Agent Advantage Decomposition理论，这时我们将不再需要精心假设价值/优势函数的拆分方式。对于任何合作式MDP，下式都成立：

【图片：/2022-09-05-14-30-45-image.png" alt="" width="317">

与value decomposition中的QPLEX（拆分优势函数的一种变体）对比：

【图片：/2022-09-05-14-31-46-image.png" title="" alt="" width="482">

注意，在上述的sequential update中，智能体可以以任意顺序排列，不局限于特定顺序。

这种更新方式意味着各个agent只需要最大化自己的local advantage，即可使整体最优。

### 单调性保证

有了上述的Multi-Agent Advantage Decomposition，我们就可以推出多机情况下的单调更新算法。遵照这种方式，我们可以保证joint reward在更新过程中单调不减。

【图片：/2022-09-05-14-17-13-image.png" title="" alt="" width="505">

其中，【图片：/2022-09-05-14-45-13-image.png" title="" alt="" width="545">，是优势函数的期望。

如果推过TRPO的单调性的话，上述内容会更好理解。

【图片：\2022-09-05-18-13-22-image.png)

具体更新算法如下：

【图片：\2022-09-05-14-51-25-image.png)

### multi-modality

除了单调性之外，auto-regressive/sequential update还有一个好处，就是可以让policy足够diverse，一次学到多个可能的最优策略。

在XOR问题的基础上，可以引申出permutation game的概念。

【图片：/2022-09-05-15-02-06-image.png" alt="" width="400">

对于independent policy来说，policy是确定性的，熵为0；而对于auto-regressive policy而言，熵为【图片：/2022-09-05-15-03-43-image.png" title="" alt="" width="117">。

可视化4-agent的permutation game结果，如下。

【图片：/2022-09-05-15-06-03-image.png" title="" alt="" width="649">

## HATRPO/HAPPO

### HATRPO

Heterogeneous-Agent Trust Region Policy Optimisation。融合了sequential update+TRPO。

【图片：/2022-09-05-15-12-42-image.png" title="" alt="" width="644">

与TRPO对比：

【图片：/D:/Desktop/MAT/TRPO.jpg" title="" alt="" width="632">

主要的区别在于对优势函数进行了序列化拆分，引入了$M$这一项。

### HAPPO

Heterogeneous-Agent Proximal Policy Optimisation。为了避免计算KL-divergence的Hessian矩阵【图片：/2022-09-05-15-08-25-image.png" alt="" width="50">，减少运算量，这里使用PPO的clip思想对运算进行近似。此时，优化的目标为：

【图片：/2022-09-05-14-55-58-image.png" title="" alt="" width="646">

其中，【图片：/2022-09-05-14-56-42-image.png" title="" alt="" width="248">。

与MAPPO对比：

【图片：/2022-09-05-14-55-39-image.png" title="" alt="" width="556">

可以看到，HAPPO在计算期望时，需要考虑到最近更新的agent的策略。

### 实验结果

SMAC & MuJoCo域上表现都非常好，但是SMAC不够难，所以与其他算法差距不大。MuJoCo中多个agent是异质的，所以HATRPO/HAPPO表现显著更好，而且agent数量越多，差距越大。

【图片：/2022-09-05-16-49-02-image.png" title="" alt="" width="645">

【图片：/2022-09-05-16-50-54-image.png" title="" alt="" width="648">

## revisiting MARL

### attention机制

每个agent需要得到前面agent的动作序列以及自己的local observation。这里引入attention机制处理action序列，可以更好地提取动作序列的特征以及agent之间动作的关系。同时，运用attention可以让表征的维数不随着动作序列的长短改变而改变，从而可以运用parameter sharing。

attention：常用于NLP相关工作，如翻译。在encoder-decoder的模型中，我们将一个序列编码为一个表征，再通过解码器转换为一组序列。为了帮助模型掌握序列中的重要信息，解码器在解码的每一步都评价序列中的各部分的重要性，从而使解码器可以关注到序列的各个部分。

### 实验结果

auto-regressive模型可以更好地促进agent间合作。

下图为bridge游戏结果。红块、蓝块一起过桥。auto-regressive policy会产生多种过桥方式，但是independent policy总是让红块先走。

【图片：/2022-09-05-16-54-43-image.png" title="" alt="" width="400">

在SMAC上，两个agent轮流向敌人射击，让敌人不停在二者间徘徊；使用independent policy的agent则会到处跑，保持与敌人的距离。面对多个敌人，auto-regressive policy让agents散开，从而分散敌军的攻击；independent policy则无法学会分而治之。

【图片：/2022-09-05-17-02-43-image.png" title="" alt="" width="378">

【图片：/2022-09-05-17-04-25-image.png" alt="" width="381">

在GRF上，auto-regressive policy可以让agent配合传球进攻，但是independent policy中是一个agent直接射门。

【图片：/2022-09-05-17-06-50-image.png" title="" alt="" width="433">

## MAT

Multi-Agent Transformer。其优势在于：

- 与MAPPO相比，可以训练heterogeneous agents；

- 与HAPPO相比，可以并行训练，效率更高。

### Transformer模型结构

Transformer自从诞生起来就引发了广泛的关注，性能非常卓越。主要包括多头自注意力机制、残差连接、层归一化、前馈全连接模块等基本单元。

【图片：/2022-09-05-15-50-18-image.png" alt="" width="317">

### MAT结构

observation到action的映射很像语言翻译！这里将joint observation视作input，序列化encode后放入decoder得到序列化action作为output。

【图片：\2022-09-05-16-14-18-image.png)

值得注意的是，在训练阶段，所有agent的数值运算与更新可以并行进行（全部action早已存在buffer之中，只需要加mask即可呈现出auto-regressive效果），所以运算速度会更快。

为了更好地满足CTDE的要求，与先前的算法作fair comparison，这里引入了MAT-dec，即把decoder换成各agent share-parameter的简单mlp。但是，MAT-dec模型仍然与CTDE不那么相似，毕竟encoder已经捕捉到了各个agent之间的互动和联系。

### 实验结果

#### 更优的策略

SMAC，MuJoCo，Bi-DexHand和GRF上均可以取得比HAPPO/MAPPO更好的结果，意味着对于homogeneous和heterogeneous的任务，MAT都可以学到更好的策略。

【图片：/2022-09-05-17-08-55-image.png" title="" alt="" width="649">

#### few-shot learning

在SMAC简单任务上训练，直接放到难任务上evaluate；在MuJoCo环境中训练好之后让部分关节坏掉，再进行evaluate。

这意味着MAT模型有更好的泛化能力。

【图片：/2022-09-05-17-15-23-image.png" title="" alt="" width="647">

## T-PPO

Transformed PPO。

### 加入distill

【图片：\2022-09-05-16-25-05-image.png)

在training阶段，策略【图片：/2022-09-05-16-42-38-image.png" alt="" width="50">主要包含两部分，一部分是从多头注意力机制这里引入的前面几个agent的动作，另一部分是从自己的trajectory里面学到的策略。在训练的时候，用自己的策略算KL，可以减少其他agent的行为对于这个agent的影响。

在inference阶段，为了保证真·decentralized的执行方式，即agent只根据自己的observation决定行为，改为使用【图片：/2022-09-05-16-46-58-image.png" title="" alt="" width="50">推断下一步动作。这个策略是通过behavior cloning得到的。

### 实验结果

在SMAC与GRF上进行了测试。证明：sequential update有用，可以学到最优策略；distill不影响inference的performance。

【图片：/2022-09-05-17-18-40-image.png" title="" alt="" width="648">

【图片：/2022-09-05-17-21-29-image.png" title="" alt="" width="648">
