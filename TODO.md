## Roadmaps
- [x] make check job under control of the same submit system
- [ ] good abstraction on resource management (tmp files can also be a resource!)
- [x] slurm plugin for check and submit
- [x] exit of main if all jobs are checked
- [ ] docs for code
- [ ] manuals for cli
- [ ] more sophisticated print or logger system
- [ ] increase task coverage for future CI and collaboration
- [x] add pre and post hooks for main
- [ ] more neat exception hierachy and code assignment

## Small tweaks
- [x] absorted state and absorting_ts for tasks in history.json
- [x] excuatble version tracking
- [x] strict version fix checking by hashing the file
- [x] default job_count limitation (one line impl in sslurm)
- [ ] add option on sslurm plugin for directly rendering files ``_from="template"``

## Thoughts and discussions

- [ ] input and output information: write in history.json or keep the convention, which is better?
- [x] add mechanism that one can manually add job naturally (seems current setup is good enough for this, just run kickstart again at anytime)
