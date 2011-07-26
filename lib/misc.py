import hachoir_core
import parser


class TorrentStripper(parser.Generic_parser):
    '''
        A torrent file looks like:
        -root
            -start
            -announce
            -announce-list
            -comment
            -created_by
            -creation_date
            -encoding
            -info
            -end
    '''
    def remove_all(self):
        for field in self.editor['root']:
            if self._should_remove(field):
                #FIXME : hachoir does not support torrent metadata editing :<
                del self.editor['/root/' + field.name]
        hachoir_core.field.writeIntoFile(self.editor,
            self.filename + parser.POSTFIX)
        self.do_backup()

    def is_clean(self):
        for field in self.editor['root']:
            if self._should_remove(field):
                return False
        return True

    def get_meta(self):
        metadata = {}
        for field in self.editor['root']:
            if self._should_remove(field):
                try:  # FIXME
                    metadata[field.name] = field.value
                except:
                    metadata[field.name] = 'harmful content'
        return metadata

    def _should_remove(self, field):
        if field.name in ('comment', 'created_by', 'creation_date', 'info'):
            return True
        else:
            return False
