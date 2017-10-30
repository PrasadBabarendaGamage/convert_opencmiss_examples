import os
from string import Template
import shutil
from subprocess import Popen, PIPE

OLD_EXAMPLE_PATH = 'old-examples/FiniteElasticity-Selection'
NEW_EXAMPLE_PATH = 'new-examples'
EXAMPLE_TEMPLATE_PATH = '../OpenCMISS-examples-template'
IGNORE_PATTERNS = ('.pyc', 'CVS', '.git', 'tmp', '.svn')
CWD = os.getcwd()


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def load_template(path, template_name):
    template_file = open(os.path.join(path, template_name))
    return Template(template_file.read())


def write_template(path, template_name, result):
    fh = open(
        os.path.join(path, template_name), 'w')
    fh.write(result)
    fh.close()


def create_example(old_example_name, example_name, templates, synopsis, addDocs=True):
    print example_name
    new_example_path = os.path.join(NEW_EXAMPLE_PATH, example_name.lower())
    if os.path.exists(new_example_path):
        shutil.rmtree(new_example_path)
    os.makedirs(new_example_path)
    copytree(EXAMPLE_TEMPLATE_PATH,
             new_example_path,
             ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))

    # Copy old example src to new src folder
    old_source_filename = os.path.join(OLD_EXAMPLE_PATH, old_example_name,
                                       'Fortran', 'src',
                                       'FortranExample.f90')
    new_source_path = os.path.join(new_example_path, 'src', 'fortran')
    shutil.copyfile(old_source_filename,
                    os.path.join(new_source_path,
                                 example_name.lower() + '.F90'))
    os.remove(os.path.join(new_source_path, 'ZZZZZZZZ.F90'))

    # Update cmake files
    d = {'example_name': example_name.lower()}
    result = templates['root_cmake_lists']['template'].substitute(d)
    write_template(new_example_path, templates['root_cmake_lists']['filename'],
                   result)

    d = {'example_name': example_name.lower()}
    result = templates['src_cmake_lists']['template'].substitute(d)
    write_template(new_source_path, templates['src_cmake_lists']['filename'],
                   result)

    # Update readme
    d = {'example_name': example_name,
         'example_name_header': '=' * len(example_name),
         'external_sources': 'None',
         'short_description': synopsis['short_description'],
         'long_description': synopsis['long_description']}
    result = templates['readme']['template'].substitute(d)
    write_template(new_example_path, templates['readme']['filename'], result)
    shutil.move(os.path.join(new_example_path, 'README.template.rst'),
                os.path.join(new_example_path, 'README.rst'))

    # Update docs
    if addDocs:
        d = {'example_name': example_name.lower()}
        result = templates['docs_index']['template'].substitute(d)
        write_template(os.path.join(new_example_path, 'docs'),
                       templates['docs_index']['filename'], result)

        d = {'example_name': example_name.lower(),
             'author': 'Thiranja Prasad Babarenda Gamage', 'version': 0.1,
             'description': synopsis['short_description']}
        result = templates['docs_conf']['template'].substitute(d)
        write_template(os.path.join(new_example_path, 'docs'),
                       templates['docs_conf']['filename'], result)

def run_example(example_name):
    new_example_path = os.path.join(NEW_EXAMPLE_PATH, example_name.lower())
    new_source_path = os.path.join(new_example_path, 'src', 'fortran')
    build_path = new_example_path + '_build'
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.makedirs(build_path)

    os.chdir(build_path)
    command = 'cmake -DOpenCMISSLibs_DIR=/home/psam012/opt/OpenCMISS/main/opencmiss/install ../{0}'.format(
        example_name.lower())
    # os.system(command)
    # print command
    # os.system('make')
    # cmd = os.path.join('src', 'fortran', example_name.lower())
    # p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    # stdout, stderr = p.communicate()
    # print stdout
    # print stderr
    os.chdir(CWD)
    #
    # fh1 = open(os.path.join(new_source_path, 'expected_results', 'stdout.txt'), 'w')
    # fh1.write(stdout)
    # fh1.close()
    #
    # fh1 = open(os.path.join('../', '{0}_stderr.txt'.format(example_name.lower())), 'w')
    # fh1.write(stderr)
    # fh1.close()


if __name__ == "__main__":

    old_example_list = ['CylinderInflation',
                        'Cantilever',
                        'UniAxialExtension',
                        'SimpleShear',
                        'ActiveContraction']

    new_example_list = ['cylinder_inflation',
                    'cantilever',
                    'uniaxial_extension',
                    'simple_shear',
                    'active_contraction']

    synopses = [{'short_description': 'Cylinder inflation.',
                 'long_description': ''},
                {'short_description': 'Cantilever beam under gravity loading.',
                 'long_description': ''},
                {'short_description': 'Uniaxial extension of a cube',
                 'long_description': ''},
                {'short_description': 'Simple shear of a cube',
                 'long_description': ''},
                {'short_description': 'Active contraction',
                 'long_description': ''}]

    # Create templates
    templates = {}

    template = {}
    template['filename'] = 'CMakeLists.txt'
    template['template'] = load_template(
        os.path.join(EXAMPLE_TEMPLATE_PATH),
        template['filename'])  # $example_name
    templates['root_cmake_lists'] = template

    template = {}
    template['filename'] = 'CMakeLists.txt'
    template['template'] = load_template(
        os.path.join(EXAMPLE_TEMPLATE_PATH, 'src/fortran'),
        template['filename'])  # $example_name
    templates['src_cmake_lists'] = template

    template = {}
    template['filename'] = 'README.template.rst'
    template['template'] = load_template(
        os.path.join(EXAMPLE_TEMPLATE_PATH), template[
            'filename'])  # $example_name ${example_name_header} ${external_sources} ${short_description} ${long_description}
    templates['readme'] = template

    template = {}
    template['filename'] = 'index.rst'
    template['template'] = load_template(
        os.path.join(EXAMPLE_TEMPLATE_PATH, 'docs'),
        template['filename'])  # $example_name
    templates['docs_index'] = template

    template = {}
    template['filename'] = 'conf.py'
    template['template'] = load_template(
        os.path.join(EXAMPLE_TEMPLATE_PATH, 'docs'),
        template[
            'filename'])  # $example_name ${author} ${version}
    templates['docs_conf'] = template

    for idx, new_example_name in enumerate(new_example_list):
        synopsis = synopses[idx]
        old_example_name = old_example_list[idx]
        create_example(old_example_name, new_example_name, templates, synopsis, addDocs=False)
        run_example(new_example_name)
