## Roadmaps
- [x] make check job under control of the same submit system
- [ ] good abstraction on resource management (tmp files can also be a resource!)
- [x] slurm plugin for check and submit
- [x] exit of main if all jobs are checked
- [x] docs for code
- [ ] manuals for cli
- [ ] more sophisticated print or logger system
- [x] increase task coverage for future CI and collaboration
- [x] CI slurm setup
- [x] add pre and post hooks for main
- [ ] more neat exception hierachy and error code assignment
- [ ] more on fault tolerance and compatible beyond check_, (eg, resolve_)
- [x] make slurmoo component more general and robust
- [x] plugins support linux background job
- [ ] powerful report summary within subway query interface

## Small tweaks
- [x] absorted state and absorting_ts for tasks in history.json
- [x] excuatble version tracking
- [x] strict version fix checking by hashing the file
- [x] default job_count limitation (one line impl in sslurm)
- [x] add option on sslurm plugin for directly rendering files ``_from="template"``
- [x] node list tracking for slurmoo

## Thoughts and discussions

- [ ] input and output information: write in history.json or keep the convention, which is better?
- [ ] is there, by any chance, keyboard interrupt of main_rt would make things confused when run main_rt again? (seems the answer is yes, an ugly way out: increase the sleep time interval which is ok for long running task)
- [x] add mechanism that one can manually add job naturally (seems current setup is good enough for this, just run kickstart again at anytime)
- [ ] dot in query and ~ in render, make they same in API and deeper level or leave it as it is