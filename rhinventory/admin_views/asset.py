from math import ceil

from flask import redirect, request, flash, url_for
from wtforms import RadioField
from flask_admin import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.actions import action
from flask_login import current_user
from sqlalchemy import desc

from rhinventory.extensions import db
from rhinventory.admin_views.model_view import CustomModelView
from rhinventory.db import Category, Medium, Asset, get_next_file_batch_number
from rhinventory.forms import FileForm

RATING_OPTIONS = [(0, 'unknown'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
class RatingField(RadioField):
    def __init__(self, **kwargs):
        super().__init__(render_kw={'class': 'rating-field'}, **kwargs)
        self.choices = RATING_OPTIONS
        self.coerce = int
        self.default = 0

class AssetView(CustomModelView):
    form_overrides = {
        'condition': RatingField,
        'functionality': RatingField,
    }
    form_excluded_columns = ('metadata', 'logs', 'transactions')
    form_edit_rules = (
        'organization',
        'category',
#        'custom_code',
        'name',
        'manufacturer',
#        'location',
        'hardware_type',
        'medium',
        'model',
        'serial',
#        'condition',
#        'functionality',
#        'status',
        'note',
        'parent',
        'children',
    )
    form_create_rules = form_edit_rules
    form_args = {
        'category': {
            'query_factory': lambda: Category.query.order_by(
                Category.id.asc()
            )
        },
        'medium': {
            'query_factory': lambda: sorted(
                Medium.query.order_by(Medium.name.asc()).all(),
                key=lambda m: m.name[0] in "0123456789"
            )
        },
    }

    can_view_details = True
    column_filters = [
        'category.name',
        'medium.name',
        'hardware_type.name',
        'name',
        'manufacturer',
        'parent.id',
    ]
    column_searchable_list = [
        'name',
        'serial',
    ]
    column_list = [
        'id',
        'location',
        'category',
        'custom_code',
        'medium',
        'hardware_type',
        'name',
        'manufacturer',
        'serial',
        #'condition',
        #'functionality',
        #'status',
        'parent',
        'transactions',
    ]
    column_sortable_list = [
        'id',
        'name',
        'manufacturer',
        'medium',
        'serial',
        'condition',
        'functionality',
        'status',
        'parent',
    ]
    column_default_sort = ('id', True)
    column_choices = {
        'condition': RATING_OPTIONS,
        'functionality': RATING_OPTIONS,
    }
    can_export = True

    list_template = "admin/asset/list.html"
    details_template = "admin/asset/details.html"

    def on_model_change(self, form, instance, is_created):
        if is_created:
            if not instance.custom_code:
                last_category_asset = db.session.query(Asset) \
                    .filter(Asset.category_id == instance.category.id, Asset.custom_code != None) \
                    .order_by(desc(Asset.custom_code)).limit(1).scalar()

                if last_category_asset:
                    instance.custom_code = int(last_category_asset.custom_code) + 1
                else:
                    instance.custom_code = 1

        super().on_model_change(form, instance, is_created)

    def get_save_return_url(self, model=None, is_created=False):
        return self.get_url('.details_view', id=model.id)

    def _get_gallery_url(self, view_args):
        """
            Generate page URL with current page, sort column and
            other parameters.
            :param view:
                View name
            :param view_args:
                ViewArgs object with page number, filters, etc.
        """
        page = view_args.page or None
        desc = 1 if view_args.sort_desc else None

        kwargs = dict(page=page, sort=view_args.sort, desc=desc, search=view_args.search)
        kwargs.update(view_args.extra_args)

        if view_args.page_size:
            kwargs['page_size'] = view_args.page_size

        kwargs.update(self._get_filters(view_args.filters))

        return self.get_url('.gallery_view', **kwargs)

    @expose('/gallery/')
    def gallery_view(self):
        """
            List view
        """
        if self.can_delete:
            delete_form = self.delete_form()
        else:
            delete_form = None

        # Grab parameters from URL
        view_args = self._get_list_extra_args()

        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get page size
        page_size = view_args.page_size or self.page_size

        # Get count and data
        count, data = self.get_list(view_args.page, sort_column, view_args.sort_desc,
                                    view_args.search, view_args.filters, page_size=page_size)

        list_forms = {}
        if self.column_editable_list:
            for row in data:
                list_forms[self.get_pk_value(row)] = self.list_form(obj=row)

        # Calculate number of pages
        if count is not None and page_size:
            num_pages = int(ceil(count / float(page_size)))
        elif not page_size:
            num_pages = 0  # hide pager for unlimited page_size
        else:
            num_pages = None  # use simple pager

        # Various URL generation helpers
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None

            return self._get_gallery_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1

            return self._get_gallery_url(view_args.clone(sort=column, sort_desc=desc))

        def page_size_url(s):
            if not s:
                s = self.page_size

            return self._get_gallery_url(view_args.clone(page_size=s))

        # Actions
        actions, actions_confirmation = self.get_actions_list()
        if actions:
            action_form = self.action_form()
        else:
            action_form = None

        clear_search_url = self._get_gallery_url(view_args.clone(page=0,
                                                              sort=view_args.sort,
                                                              sort_desc=view_args.sort_desc,
                                                              search=None,
                                                              filters=None))

        return self.render(
            'admin/asset/gallery.html',
            data=data,
            list_forms=list_forms,
            delete_form=delete_form,
            action_form=action_form,

            # List
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            list_row_actions=self.get_list_row_actions(),

            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            can_set_page_size=self.can_set_page_size,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            default_page_size=self.page_size,

            # Sorting
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,

            # Search
            search_supported=self._search_supported,
            clear_search_url=clear_search_url,
            search=view_args.search,
            search_placeholder=self.search_placeholder(),

            # Filters
            filters=self._filters,
            filter_groups=self._get_filter_groups(),
            active_filters=view_args.filters,
            filter_args=self._get_filters(view_args.filters),

            # Actions
            actions=actions,
            actions_confirmation=actions_confirmation,

            # Misc
            enumerate=enumerate,
            get_pk_value=self.get_pk_value,
            get_value=self.get_list_value,
            return_url=self._get_gallery_url(view_args),

            extra_args={}
        )
    
    # Overridden https://flask-admin.readthedocs.io/en/latest/_modules/flask_admin/model/base/#BaseModelView.details_view
    @expose('/details/')
    def details_view(self):
        return_url = get_redirect_target() or self.get_url('.index_view')

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)
        
        if id.startswith("RH"):
            id = id[2:]

        model = self.get_one(id)

        if model is None:
            flash('Record does not exist.', 'error')
            return redirect(return_url)

        template = self.details_template

        batch_number = get_next_file_batch_number()
        file_form = FileForm(batch_number=batch_number)

        return self.render(template,
                            model=model,
                            details_columns=self._details_columns,
                            get_value=self.get_detail_value,
                            return_url=return_url,
                            file_form=file_form)
                    
    
    @action('create_transaction', 'Create transaction')
    def create_transaction(self, asset_ids):
        return redirect(url_for('transaction.create_view', asset_id=repr(asset_ids)))


    def create_form(self, obj=None):
        form = super(type(self), self).create_form()

        if not form.organization.data:
            form.organization.data = current_user.organization

        return form