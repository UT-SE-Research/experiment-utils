import getpass
import json
import requests
import shutil
import subprocess
import sys

from find import find_file

# From list of slugs, filter for Maven projects
def filter_for_maven_projects(slugs):
    maven_projects = []
    for project in slugs:
        request = 'https://github.com/' + project + '/blob/master/pom.xml'  # Assume branch of master only...
        response = requests.get(request)
        # If can get a response, then project is (probably) Maven
        if response.ok:
            # Some tweaking to get the actual project slug, in case of redirects
            actual_project_slug = response.url.replace('https://github.com/', '').replace('/blob/master/pom.xml', '')
            maven_projects.append(actual_project_slug)
    return maven_projects

# From list of slugs, filter for Gradle projects
def filter_for_gradle_projects(slugs):
    gradle_projects = []
    for project in slugs:
        request = 'https://github.com/' + project + '/blob/master/build.gradle' # Assume branch of master only...
        response = requests.get(request)
        # If can get a response, then project is (probably) Maven
        if response.ok:
            # Some tweaking to get the actual project slug, in case of redirects
            actual_project_slug = response.url.replace('https://github.com/', '').replace('/blob/master/build.gradle', '')
            gradle_projects.append(actual_project_slug)
    return gradle_projects

# From list of valid Maven projects, filter for ones that are on Travis
def filter_for_travis_projects(maven_projects):
    travis_projects = []
    for project in maven_projects:
        # First check if on GitHub they have a .travis.yml
        request = 'https://github.com/' + project + '/blob/master/.travis.yml'  # Assume branch of master only...
        response = requests.get(request)
        # If cannot get a response, then project is not Travis, so can skip
        if not response.ok:
            continue

        # Otherwise, hit the Travis API to double-check it has been activated
        request = 'https://api.travis-ci.org/repos/' + project
        response = requests.get(request)
        if response.ok:
            try:
                data = json.loads(response.text, encoding = 'utf-8')
            except ValueError:
                # Something went wrong, Travis returns some weird image of sorts, so skip
                print 'TRAVIS FILTER VALUE ERROR FOR ' + project
                continue
            if data['active']:
                travis_projects.append(project)
    return travis_projects

# From list of valid Travis projects, filter for ones that are multimodule
def filter_for_multimodule_projects(travis_projects):
    multimodule_projects = []
    for project in travis_projects:
        command = 'git clone https://github.com/' + project + ' tmp --depth=1'
        subprocess.call(command.split())
        if len(find_file('pom.xml', 'tmp')) > 1:
        #if len(find_file('build.gradle', 'tmp')) > 1:
            multimodule_projects.append(project)
        shutil.rmtree('tmp')
    return multimodule_projects

def main(args):
    uname = args[1] # Username
    out_file = args[2]
    passwd = getpass.getpass()

    # Get all the Java projects on GitHub
    slugs = []
    url = 'https://api.github.com/search/repositories?q=language:java&sort=stars&order=desc&per_page=100'
    #for i in range(1, 36):
    for i in range(1, 2):
        suffix = '&page=' + str(i)
        request = url + suffix
        response = requests.get(request, auth=(uname, passwd))
        if response.ok:
            data = json.loads(response.text)
            for k in data['items']:
                slugs.append(k['full_name'])
        else:
            break

    print 'ALL PROJECTS:', len(slugs)

    # Check if the project is a Maven project by merely checking if a link to the pom.xml can be accessed
    maven_projects = filter_for_maven_projects(slugs)
    print 'MAVEN PROJECTS:', len(maven_projects)

    # Check if the Maven projects are on Travis, by hitting the Travis API and checking that it's active
    travis_projects = filter_for_travis_projects(maven_projects)
    print 'TRAVIS PROJECTS:', len(travis_projects)

    # For each such project, check if it's multi-module by checking it out and counting that it has more than one pom.xml
    multimodule_projects = filter_for_multimodule_projects(travis_projects)
    print 'MULTIMODULE PROJECTS', len(multimodule_projects)

    # Print out final filtered list of projects (the slugs)
    with open(out_file, 'w') as out:
        for project in multimodule_projects:
            out.write(project + '\n')

if __name__ == '__main__':
    main(sys.argv)
