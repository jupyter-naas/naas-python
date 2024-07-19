import os
import naas-python as naas_python
post_object = naas_python.storage.post_workspace_storage_object(
        workspace_id=workspace_id,
        storage_name="test",
        src_file="Adele.png",
        dst_file="Adele.png",
)
post_object