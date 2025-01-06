from sqlalchemy import select, and_
from sqlalchemy.orm import Session, Query, aliased

from rhinventory.api.asset.schemas import AssetSchema
from rhinventory.models.asset import Asset
from rhinventory.models.asset_attributes import AssetTag, asset_tag_table
from rhinventory.models.enums import HIDDEN_PRIVACIES, PUBLIC_PRIVACIES
from rhinventory.models.file import File, FileCategory
from rhinventory.util import print_sql_query


class InvalidAssetTag(Exception):
    """Tag doesn't exist or is otherwise invalid."""
    pass


class AssetService:

    @staticmethod
    def _ensure_privacy(query: Query, private: bool) -> Query:
        """
        Adds where clause, to respect Asset privacy settings.

        :param query: given query on Asset
        :param private: If True, shows event private items, otherwise only public.
        :return: modified query
        """
        return query.where(Asset.privacy.in_(PUBLIC_PRIVACIES if not private else PUBLIC_PRIVACIES + HIDDEN_PRIVACIES))


    @staticmethod
    def _get_asset_files(query: Query, private: bool) -> Query:
        file_privacies = PUBLIC_PRIVACIES if not private else PUBLIC_PRIVACIES + HIDDEN_PRIVACIES

        # Create aliases for each type of file
        image_file = aliased(File)
        document_file = aliased(File)
        dump_file = aliased(File)

        return (
            query
            # Outer join for image
            .outerjoin(image_file, and_(
                image_file.asset_id == Asset.id,
                image_file.category == FileCategory.photo,
                image_file.primary == True,
                image_file.privacy.in_(file_privacies)
            ))
            .add_columns(image_file.filepath.label("primary_image_path"))

            # Outer join for document
            .outerjoin(document_file, and_(
                document_file.asset_id == Asset.id,
                document_file.category == FileCategory.document,
                document_file.primary == True,
                document_file.privacy.in_(file_privacies)
            ))
            .add_columns(document_file.filepath.label("primary_document_path"))

            # Outer join for dump
            .outerjoin(dump_file, and_(
                dump_file.asset_id == Asset.id,
                dump_file.category == FileCategory.dump,
                dump_file.primary == True,
                dump_file.privacy.in_(file_privacies)
            ))
            .add_columns(dump_file.filepath.label("primary_dump_path"))
        )

    @staticmethod
    def get_single(db_session: Session, asset_id: int, private: bool = False):
        """
        Get single Asset by id.

        :param asset_id: unique Asset ID
        :return: Asset with all stuff around it for consistency.
        """
        query = select(
            Asset.id,
            Asset.name,
            Asset.model,
            Asset.note,
            Asset.serial
        ).where(Asset.id == asset_id)
        query = AssetService._ensure_privacy(query, private)
        query = AssetService._get_asset_files(query, private)

        asset = db_session.execute(query)

        return asset.fetchone()


    @staticmethod
    def list_all(db_session: Session, limit: int = 100, offset: int = 0, private=False):
        """
        List all Assets.

        Respects publicity of given assets.

        :param limit: How much assets to return (defaut 100).
        :param offset: With what offset (defaults to 0).
        :param private: If True, shows even private items (defaults to False).
        :return: List of Asset objects.
        """
        query = select(
            Asset.id,
            Asset.name,
            Asset.model,
            Asset.note,
            Asset.serial
        ).limit(limit).offset(offset)
        query = AssetService._ensure_privacy(query, private)
        query = AssetService._get_asset_files(query, private)

        assets = db_session.execute(
            query
        )

        return assets.fetchall()

    @staticmethod
    def list_by_tag(db_session: Session, tag_id: int, limit: int = 100, offset: int = 0, private=False):
        """
        List all assets with concrete tag.

        Respects publicity of given assets.

        :param tag_id: Asset tag to look up by id.
        :param limit: How much assets to return (defaut 100).
        :param offset: With what offset (defaults to 0).
        :param private: If True, shows even private items (defaults to False).
        :return: List of Asset objects with given tag.
        """

        query = (
            select(
                Asset.id,
                Asset.name,
                Asset.model,
                Asset.note,
                Asset.serial
            )
            .join(asset_tag_table, asset_tag_table.c.asset_id == Asset.id)
            .join(AssetTag, AssetTag.id == asset_tag_table.c.assettag_id)
            .where(AssetTag.id == tag_id)
            .limit(limit).offset(offset)
        )

        query = AssetService._ensure_privacy(query, private)
        query = AssetService._get_asset_files(query, private)

        assets = db_session.execute(
            query
        )

        return assets.fetchall()