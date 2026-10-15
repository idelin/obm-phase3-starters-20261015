# 文件与运行

public/main.go与go.mod为Go工程。example.jsonl与example.expected.jsonl为接口示例。observe-linux-amd64及vendor为Linux x86_64可执行观察材料，运行时保持相对路径。第三方许可证位于LICENSES。

```sh
cd public
./observe-linux-amd64 < example.jsonl
go build -o tool .
./tool < example.jsonl
```

## 时限

候选单请求运行上限30秒；build上限120秒；verifier整套上限600秒。依据为macOS arm64、Go1.24.2下的冷缓存构建3.228秒、80步观察请求8.703秒，以及两题完整验证套件63.428秒，所列上限包含留量；这些测量不代表Linux实跑。关联ProgramBench任务元数据未给出solver整轮作答时限，该预算由下游运行配置指定，不能用单请求30秒替代。
