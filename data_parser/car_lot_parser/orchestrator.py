from multiprocessing import Process

from car_lot_parser.car_worker import Worker


class Orchestrator:

    def __init__(self, client_factory, parser, batcher, db_writer, workers_count: int):
        self.workers_count = workers_count
        self.client_factory = client_factory
        self.parser = parser
        self.batcher = batcher
        self.db_writer = db_writer

    def _run_worker(self, worker_id):
        client = self.client_factory(worker_id)
        worker = Worker(client, self.parser, self.batcher, self.db_writer, worker_id)
        worker.run()

    def run(self):
        processes = []

        for worker_id in range(1, self.workers_count + 1):
            process = Process(
                target=self._run_worker,
                args=(worker_id,),
                name=f"worker-{worker_id}"
            )

            processes.append(process)
            process.start()

        for process in processes:
            process.join()
