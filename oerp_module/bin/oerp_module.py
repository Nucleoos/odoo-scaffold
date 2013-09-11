#!/usr/bin/python
import os
import sys
import argparse

#~ config repos

repo_data = {
    'addons-vauxoo': {
        'name': 'addons-vauxoo',
        'serie': '7.0',
        'group': '~vauxoo',
        'local': '~/bzr_projects/addons_vauxoo_branches/7.0-addons-vauxoo',
    },
    'vauxoo-private': {
        'name': 'vauxoo-private',
        'serie': False,
        'group': '~vauxoo-private',
        'local': '~/bzr_projects/vauxoo-private',
    },
    'ovl70': {
        'name': 'openerp-venezuela-localization',
        'serie': '7.0',
        'group': '~vauxoo',
        'local': '~/bzr_projects/_VE/ovl_branches/ovl70',
    },
    'junk': {
        'name': '~katherine-zaoral-7/+junk',
        'serie': False,
        'group': '~katherine-zaoral-7',
        'local': '~/bzr_projects/+junk/katherine-zaoral-7',
    },
}
_oerp_version_list = ['6.0', '6.1', '7.0']


class oerp_template(object):

    """
    Contains the files templates
    """

    license_msg = \
"""#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
############# Credits #########################################################
#    Coded by: %s
#    Planified by: %s
#    Audited by: %s
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
"""

    model_py = \
"""
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import tools


class %s(osv.Model):

    _name = '%s'
    _description = _('Need to set the model name')
    _inherit = ['mail.thread']

    '''
    Need to set the model description
    '''

    _columns = {
        'name': fields.char(
            _('Name'),
            required=True,
            size=64,
            help=_('Name')),
    }

    _defaults = {
    }
"""

    wizard_py = \
"""
from openerp.osv import osv, fields
from openerp.tools.translate import _
import decimal_precision as dp


class %s_wizard(osv.TransientModel):

    _name = '%s'
    _description = _('Need to set the model name')

    '''
    Need to set the model description
    '''

    _columns = {
    }

    _defaults = {
    }

"""

    openerp_py = \
"""
{
    'name': '%s',
    'version': '1.0',
    'author': 'Vauxoo C.A.',
    'website': 'http://www.openerp.com.ve',
    'category': '',
    'description': '''
''',
    'depends': ['base', 'mail'],
    'data': [],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,
}"""


class oerp_module(object):

    directory_list = [
        'model',
        'view',
        'wizard',
        'i18n',
        'workflow',
        'data',
        'demo',
        'doc',
        'doc/images',
        'test',
        'report',
        'security',
        'static',
        'static/description',
        'static/src',
        'static/src/js',
        'static/src/css',
        'static/src/xml',
        'static/src/img']

    def __init__(self, name, developer, parent_repo, version):
        """
        iniciialization of the module
        @param name: new module name
        @param version: the version of the new model
        @param developer:
        @param repository:
        """

        #~ TODO: add the manage a list of developers, planners and auditors

        print '\n... Checking Script Parameters'
        self.name = name
        self.directory = name
        self.developer = developer

        if version in _oerp_version_list:
            self.version = version
        else:
            raise Exception("Bad parameters. '%s' Its not a valid openerp "
                            "version" % (version,))

        if parent_repo in repo_data:
            self.branch_name = '%s-dev-%s-%s' % (version, name, developer)
            self.parent_repo = repo_data[parent_repo].copy()
            self.repo_name = repo_data[parent_repo]['name']
            self.repo_group = repo_data[parent_repo]['group']
            self.repo_serie = repo_data[parent_repo]['serie']
        else:
            raise Exception("Bad paramenters. The repository %s does not exist"
                            " in the current script configuration. Please add"
                            " the repo to the repo_data dictonary." % (
                            parent_repo,))

        self.path = '%s/%s' % (self.branch_name, self.directory)
        self.template = oerp_template()
        self.license_msg = self.set_license_msg()
        return None

    def create_branch(self):
        """
        Create a new branch for the development module using the parent repo
        serie branch like point of start:
        1. create module new local branch by copying the parent local repo
        2. create module new cloud branch by copying the parent cloud repo
        3. link both local and cloud branches
        4. mark new branch with a init revision for new module
        """
        # TODO update parent repo before copy for the new module
        # TODO OPT add branch detail using python launchpad-bzr lib

        print '... Creating branch for the new module'

        print 'Create new module local branch'
        os.system('cp %s %s -r' % (
            self.parent_repo['local'], self.branch_name))
        os.system('echo \'\' | cat - > %s/.bzr/branch/branch.conf'% (self.branch_name,))

        print 'Create new module cloud branch'
        os.system('bzr branch lp:%s/%s/%s lp:%s/%s/%s' % (
            self.repo_group, self.repo_name, self.repo_serie,
            self.repo_group, self.repo_name, self.branch_name))

        print 'Linking local and cloud branches'
        os.system('cd %s && bzr pull lp:%s/%s/%s --remember' % (
            self.branch_name, self.repo_group, self.repo_name,
            self.branch_name))

        print 'Add mark revision of the begining of the new module dev'
        os.system('cd %s && bzr ci -m "%s" --unchanged' % (
            self.branch_name,
            '[INIT] new branch for development of %s module.' % (self.name,)))
        os.system('cd %s && bzr push lp:%s/%s/%s --remember' % (
            self.branch_name, self.repo_group, self.repo_name,
            self.branch_name))
        return True

    def create_main_directory(self):
        """
        Create the module main directory with the module name.
        """
        print '... Create module main directory'
        os.system('mkdir %s' % (self.path))
        return True

    def create_directories(self):
        """
        Create the base directories taking into account the directory config
        list.
        """
        print '... Create module structure dicectories'
        for strc_dir in self.directory_list:
            os.system('mkdir %s/%s' % (self.path, strc_dir))
        return True

    def create_base_files(self):
        """
        Create the base files for the module, include de init files, the
        openerp file and the index.html and the icon.png file.
        """
        print '... Create module base files'
        self.create_init_files()
        self.create_openerp_file()
        self.add_icon_file()
        self.create_index_html_file()
        return True

    def create_init_files(self):
        """
        Create init files with the license set taking into account the module
        developers, planners and auditors.
        """
        init_files = {
            '__init__.py': 'import model\nimport wizard',
            'model/__init__.py': '',
            'wizard/__init__.py': '',
        }

        print '... Creating init files'
        for (new_file, content) in init_files.iteritems():
            os.system('echo """%s""" | cat - > %s' % (
                self.license_msg + content, '%s/%s' % (self.path, new_file)))
        return True

    def create_openerp_file(self):
        """
        Create the openerp descriptive file
        """
        content = self.template.openerp_py % (self.name,)

        print '... Create the openerp descriptive file'
        os.system('echo """%s""" | cat - > %s' % (
            self.license_msg + content, '%s/__openerp__.py' % (self.path,)))
        return True

    def add_icon_file(self):
        """
        Add the icon.png file to the module.
        """
        print '... Adding module icon'
        os.system('cp %s/src/icon.png %s/static/src/img/' % (sys.argv[0].split('bin')[0], self.path))
        return True

    def create_index_html_file(self):
        """
        Touch to create a clean index.html file in the
        static/description/index.html
        """
        print '... Creating a blanck index.html for module description'
        os.system('touch %s/static/description/index.html' % (self.path,))
        return True

    def create_py_files(self, file_py):
        """
        """
        print '... Create the model and wirzard py files'
        new_file = '%s/%s.py' % (file_py, self.name)
        content = self.license_msg + getattr(
            self.template, file_py + '_py') % (
                self.name, self.name.replace('_', '.'))
        os.system('echo """%s""" | cat - > %s' % (
            content, '%s/%s' % (self.path, new_file)))
        return True

    def set_license_msg(self):
        """
        Take the default template for license and add the developers, planners
        and auditors info.
        """

        license_msg = self.template.license_msg

        developer_str = 'Katherine Zaoral <kathy@vauxoo.com>'
        planner_str = 'Humberto Arocha <hbto@vauxoo.com>'
        auditor_str = 'Humberto Arocha <hbto@vauxoo.com>'

        return license_msg % (developer_str, planner_str, auditor_str)

    def branch_changes_apply(self):
        """
        Create one revision to commit the structure and basic module files
        after the creation from scratch.
        """

        print '... Commit the module incialization of strcutre and basic files'
        os.system('cd %s && bzr add && bzr ci -m "%s"' % (
            self.path, '[ADD] Module structure and basic files'))
        return True

    def push_changes(self):
        """
        Push changes of the parent branch at the cloud 
        """
        print '... Push changes to parent branch at cloud'
        os.system('bzr push :parent' % (
            self.path, '[ADD] Module structure and basic files'))
        return True


def argument_parser():
    """
    This function create the help command line and manage and filter the
    parameters of this program (default values, choices values)
    """
    parser = argparse.ArgumentParser(
        prog='new_module_openerp',
        description='Create new openerp module structure and basic files.',
        epilog="""
Openerp Developer Comunity Tool
Development by Vauxoo Team (lp:~vauxoo)
Coded by Katherine Zaoral <kathy@vauxoo.com>.
Source code at lp:~katherine-zaoral-7/+junk/oerp_module.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'name',
        metavar='MODULE_NAME',
        type=str,
        help='name of the module to create.')
    parser.add_argument(
        '-s', '--branch-suffix',
        metavar='DEVELOPER_ACRONYM',
        type=str,
        help=str('branch suffix. Generally developer acronym name. It use when'
                 ' creating the branch for identify the team user owner in a'
                 ' simply way'),
        required=True)
    parser.add_argument(
        '-r', '--parent_repo',
        metavar='PARENT_REPO',
        type=str,
        help='name of parent repo',
        choices=repo_data.keys())
    parser.add_argument(
        '-ov', '--oerp-version',
        metavar='VERSION',
        type=str,
        choices=_oerp_version_list,
        help='Openerp version number')
    parser.add_argument(
        '-c', '--create-structure', action='store_true',
        help='inicializate module / create new directory with basic files')
    parser.add_argument(
        '-b', '--branch-create', action='store_true',
        help='create a branch copy in the parent repo that will holds the new'
             ' module')
    parser.add_argument(
        '-a', '--append-file',
        metavar='TYPE_OF_FILE',
        type=str,
        help='append a file to the module',
        choices=['model', 'wizard'])

    parser.set_defaults(
        oerp_version='7.0',
        parent_repo='addons-vauxoo'
    )

    return parser.parse_args()


def main():

    args = argument_parser()

    print'\n... Configuration of Parameters Set'
    for (parameter, value) in args.__dict__.iteritems():
        print '%s = %s' % (parameter, value)

    module = oerp_module(
        args.name, args.branch_suffix, args.parent_repo, args.oerp_version)

    if args.branch_create:
        module.create_branch()

    if args.create_structure:
        module.create_main_directory()
        module.create_directories()
        module.create_base_files()

    if args.append_file:
        module.create_py_files(args.append_file)

        #~ module.branch_changes_apply()

if __name__ == '__main__':
    main()
