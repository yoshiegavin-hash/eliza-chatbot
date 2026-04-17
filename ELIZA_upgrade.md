# ELIZA 升级笔记

## 升级内容

### 1. 新增 4 条对话规则

| 规则 | 匹配关键词 | 响应示例 |
|------|-----------|---------|
| 工作/职业 | work, job, career, boss, colleague, office | "How do you feel about your work?" |
| 学习/教育 | study, school, class, exam, grade, course, major, university | "What are you studying?" |
| 兴趣爱好 | hobby, sport, game, music, read, movie, paint, draw, cook | "How did you get into that?" |
| 情绪/压力 | stress, anxious, tired, burnout, overwhelm, pressure | "How do you usually cope with that feeling?" |

### 2. 上下文记忆功能

**存储的信息类型**（`memory` 字典）：

| 字段 | 提取模式 | 示例 |
|------|---------|------|
| `name` | `my name is...` / `i am called...` / `i'm...` | "feiyu" |
| `age` | `i am 22 years old` / `i'm 25` | "25" |
| `job` | `i work as...` / `i am employed...` | "software engineer" |
| `major` | `i study...` / `i major in...` | "Shanghai" |
| `hobby` | `my hobby is...` / `i like/love/enjoy...` | "coding" |

**核心函数：**

- `try_extract_memory(user_input)` — 从用户输入中自动提取关键信息并存入 `memory`
- `recall_memory(user_input)` — 根据用户提问引用记忆：
  - 显式询问（"do you know my name", "what do you know", "remember" 等）时，列出所有记住的信息
  - 随机（15%概率）主动引用名字或爱好进行对话引导

**Hobby 过滤**：`is_valid_hobby()` 排除家庭成员词汇（mother/father 等），防止 "I love my mother" 被错误存储为爱好。

---

## 遇到的问题与修复

### Bug 1: 名字记忆被随机引用覆盖
- **现象**: 问 "do you know my name?" 时返回了 hobby 信息而非名字
- **原因**: `recall_memory()` 的随机引用逻辑在显式询问时也可能触发
- **修复**: 将关键词列表扩展为 `is_explicit_recall`，显式询问时跳过随机引用

### Bug 2: 家庭成员被错误存储为 hobby
- **现象**: "I love my mother" 被存为 `hobby = "my mother."`
- **原因**: `(i like|love|enjoy)...` 匹配了任何宾语
- **修复**: 新增 `is_valid_hobby()` 函数，过滤包含家庭成员词汇的内容

### Bug 3: 标点符号污染
- **现象**: 存储的值带尾随句号（"Shanghai."）
- **原因**: `strip()` 只去空格，没去标点
- **修复**: 提取后用 `.strip(string.punctuation)` 清理

---

## 运行效果示例

```
Therapist: Hello! I'm Eliza. Tell me about yourself.

You: My name is feiyu.
Therapist: I remember that your name is feiyu.

You: I love my mother.
Therapist: Tell me more about your mother.

You: I study in Shanghai.
Therapist: What are you studying?

You: do you know my name?
Therapist: I remember that your name is feiyu.

You: I am 22 years old.
Therapist: By the way, feiyu, how does that make you feel?

You: what do you know about me?
Therapist: I remember that your name is feiyu, and you are 22 years old, and you study Shanghai.
```
