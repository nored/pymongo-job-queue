import pymongo
from datetime import datetime
import time


''' ..v2.0.0 custom exceptions '''

class JobQueueBaseError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
        
class JobQueueCreateError(JobQueueBaseError):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class JobQueueEmptyError(JobQueueBaseError):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)

class JobQueuePubError(JobQueueBaseError):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)




class JobQueue:

    # Capped collection documents can not have its size updated
    # https://docs.mongodb.com/manual/core/capped-collections/#document-size
    DONE = 'done'.ljust(10, '_')
    WAITING = 'waiting'.ljust(10, '_')
    WORKING = 'working'.ljust(10, '_')


    def __init__(self, db, silent=False, iterator_wait=None, size=None, collection_name='jobqueue'):
        """ Return an instance of a JobQueue.
        Initialization requires one argument, the database,
        since we use one jobqueue collection to cover all
        sites in an installation/database. The second
        argument specifies if to print status while waiting
        for new job, the default value is False"""
        self.db = db
        self.silent = silent
        self.collection_name = collection_name
        if not self._exists():
            if not silent:
                print ('Creating "{}" collection.'.format(self.collection_name))
            self._create(size)
        self.q = self.db[self.collection_name]
        self.iterator_wait = iterator_wait
        if self.iterator_wait is None:
            def default_iterator_wait():
                if not self.silent:
                    print ('waiting!')
                time.sleep(5)
                return True

            self.iterator_wait = default_iterator_wait

    def _create(self, size=None, capped=True):
        """ Creates a Capped Collection. """
        try:
            # size - When creating a capped collection you must specify the maximum size
            #        of the collection in bytes, which MongoDB will pre-allocate for the
            #        collection. The size of the capped collection includes a small amount
            #        of space for internal overhead.
            # max - you may also specify a maximum number of documents for the collection
            '''.. v2.0.0. capped - If size or max then capped must be True (ref tests for valid())'''
            
            if capped:
                if not size:
                    size = 100000
                self.db.create_collection(self.collection_name,
                                          capped=capped,
                                          size=size)
            else:
                ''' .. v2.0.0 this needed to be here to allow tests to create a non-capped - revisit'''
                self.db.create_collection(self.collection_name)
                
        except:
            '''..v2.0.0'''
            raise JobQueueCreateError(f"creating collection {self.collection_name}")

    def _find_opts(self):
        if hasattr(pymongo, 'CursorType'):
            return {'cursor_type': pymongo.CursorType.TAILABLE_AWAIT}   # pylint: disable=no-member
        return {'Tailable': True}

    def _exists(self):
        """ Ensures that the jobqueue collection exists in the DB. """
        return self.collection_name in self.db.list_collection_names()

    def valid(self):
        """ Checks to see if the jobqueue is a capped collection. """
        opts = self.db[self.collection_name].options()
        if opts.get('capped', False):
            return True
        return False

    def next(self):
        """ 
        Gets the next job in the queue. Marks it as started.
        Raises JobQueueEmptyError if the queue is empty
        """
        #cursor = self.q.find({'status': self.WAITING},
        #                     **self._find_opts()).limit(1)
        try:
            #row = cursor.next()
            row = self.q.find_one_and_update({
                                              'status': self.WAITING
                                             },
                                             {'$set':
                                                {'status': self.DONE,
                                                 'ts.started': datetime.utcnow(),
                                                 'ts.done': datetime.utcnow()
                                                }
                                             }
                                            )
            if row:
                return row
            else:
                '''..v2.0.0'''
                raise JobQueueEmptyError('queue empty')
        except Exception as ex:
            raise ex('getting next job')


    def pub(self, data=None):
        """ Publishes a doc to the work queue. """
        doc = dict(
            ts={'created': datetime.utcnow(),
                'started': datetime.utcnow(),
                'done': datetime.utcnow()},
            status=self.WAITING,
            data=data)
        try:
            self.q.insert_one(doc)
        except:
            '''..v2.0.0'''
            raise JobQueuePubError('could not add to queue')
        return True

    def __iter__(self):
        """ Iterates through all docs in the queue
            and waits for new jobs when queue is empty. """
        cursor = self.q.find({'status': self.WAITING},
                             **self._find_opts()).limit(1)
        get_next = True
        while get_next:
            if not cursor.alive:
                cursor = self.q.find({'status': self.WAITING},
                                     **self._find_opts()).limit(1)
            try:
                row = cursor.next()
                row = self.q.find_one_and_update(
                    {'_id': row['_id'],
                     'status': self.WAITING},
                    {'$set':
                     {'status': self.WORKING,
                      'ts.started': datetime.utcnow()}})
                if row:
                    if not self.silent:
                        print('---')
                        print('Working on job:')
                    yield row
                    self.q.update_one({'_id': row['_id']},
                                      {'$set': {'status': self.DONE,
                                                'ts.done': datetime.utcnow()}})
            except StopIteration:
                get_next = self.iterator_wait()

            except:
                row = self.q.find_one_and_update(
                    {'_id': row['_id'],
                     'status': self.WORKING},
                    {'$set':
                     {'status': self.WAITING}})
                raise


    def queue_count(self):
        """ Returns the number of jobs waiting in the queue. """
        #cursor = self.q.find({'status': self.WAITING})
        #if cursor:
        #    return cursor.count()
        '''...v2.0.0.0'''
        return self.q.count_documents({'status': self.WAITING})

    def clear_queue(self):
        """
        .. v2.0.0 changed from drop collection to delete many - otherwise next access recreates collection as uncapped
        """ 
        self.q.delete_many({})
        
