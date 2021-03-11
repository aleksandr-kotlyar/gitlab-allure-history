# gitlab-allure-history

![GitHub statistics](https://raw.githubusercontent.com/aleksandr-kotlyar/gitlab-allure-history/traffic-2021/traffic-gitlab-allure-history/in_2021.svg)
![GitHub views](https://raw.githubusercontent.com/aleksandr-kotlyar/gitlab-allure-history/traffic-2021/traffic-gitlab-allure-history/views.svg)
![GitHub views per week](https://raw.githubusercontent.com/aleksandr-kotlyar/gitlab-allure-history/traffic-2021/traffic-gitlab-allure-history/views_per_week.svg)
![GitHub clones](https://raw.githubusercontent.com/aleksandr-kotlyar/gitlab-allure-history/traffic-2021/traffic-gitlab-allure-history/clones.svg)
![GitHub clones per week](https://raw.githubusercontent.com/aleksandr-kotlyar/gitlab-allure-history/traffic-2021/traffic-gitlab-allure-history/clones_per_week.svg)

Example project using GitLab CI/CD for Allure report with history on GitLab Pages.

You can see [Allure Report](https://aleksandr-kotlyar.gitlab.io/gitlab-allure-history/) on GitLab Pages.

## GitLab CI/CD
Learn how to use GitLab CI/CD on [official docs](https://docs.gitlab.com/ce/ci/quick_start/index.html).

Here are my advices:
1. You need to create workflow in `.gitlab-ci.yml` in project root. Example workflow [.gitlab-ci.yml](https://github.com/aleksandr-kotlyar/gitlab-allure-history/blob/master/.gitlab-ci.yml).
2. This workflow uses GitLab Job artifacts to pass allure-results from job to job through 
   stages. Read more about [Job artifacts](https://docs.gitlab.com/ce/ci/pipelines/job_artifacts.html).
3. There are three stages: test, report, deploy. Read more about GitLab [Pipeline Architecture](https://docs.gitlab.com/ee/ci/pipelines/pipeline_architectures.html). 
   - test (tests execution, passing allure-results to artifacts)
   - report (generating allure-report, passing allure-report to artifacts)
   - deploy (publishing allure-report on GitLab Pages from artifacts)

## GitLab Pages
Learn how to use GitLab Pages on [official docs](https://docs.gitlab.com/ee/user/project/pages/).

Here are my advices:
1. Go to your repository Settings-> General->Visibility scroll down to Pages and ensure the 
   feature is enabled. Also, you can choose visibility for everyone or for project members only.
2. Create a separate branch which will store your allure-reports on GitLab Pages, to not store full 
   allure-report history at master. For example 'gl-pages'.
3. Create in branch 'gl-pages' a `.gitlab-ci.yml` file with job `pages`, stage `deploy` and 
   artifacts `public`, example:
   ```yaml
   stages:
    - deploy

   pages:
     image: alpine
     stage: deploy
     script:
       - echo "Publish to GitLab Pages"
     artifacts:
       paths:
         - public
   ```
4. Commit your reports with indexed report tree to 'gl-pages' `/public` directory.
5. Every time you push a commit to 'gl-pages', the 'pages' job will publish all the public 
   directory has on GitLab Pages.

## Allure Report with history on GitLab Pages
Here is how it works:

1. Job 'test' is running tests on your current branch and saves allure-results to artifacts for 
   the next job in pipeline.
2. Job 'allure':
   1. Clones 'gl-pages' branch into container with a copy of all 'gl-pages' branch files 
      (previous reports).
   2. Gets the 'history' of the last build from the same branch (if exists) into
      'allure-results' of current build.
   3. Creates 'executor.json' in 'allure-results' with build info and buildUrls in trends.
   4. Generates report with allure Commandline into job_number build folder.
   5. Creates branch-dir in 'gl-pages' `/public` directory if it's not existed yet.    
   5. Copies report into 'gl-pages' `/public/branch` directory: `/public/branch/job_number`.
   6. Generates the index files for page tree `/public` and `/public/branch`.
   7. Commits and pushes the public directory into 'gl-pages' branch into the repo.
3. And then push to branch 'gl-pages' triggers it's own job `pages` which publishes all 
   content from `/public` directory on GitLab Pages. You can open root link of GitLab Pages and 
   always see all the history of each branch and find the latest execution by the latest 
   job_number inside the branch-dir of the branch you are interested in.