# -*- coding: utf-8 -*-
import logging

import numpy as np
from sklearn.decomposition import LatentDirichletAllocation

from ._evaluation_common import MultiprocEvaluation, MultiprocEvaluationWorkerABC,\
    metric_cao_juan_2009, metric_arun_2010


AVAILABLE_METRICS = (
    'perplexity',
    'cross_validation',
    'cao_juan_2009',
    'arun_2010',
)


logger = logging.getLogger('tmtoolkit')


class MultiprocEvaluationWorkerSklearn(MultiprocEvaluationWorkerABC):
    def fit_model_using_params(self, params):
        data = self.data.tocsr()

        if self.n_folds > 1:
            logger.info('fitting LDA model from package `sklearn` with %d fold validation to data of shape %s'
                        ' with parameters: %s' % (self.n_folds, data.shape, params))

            perplexity_measurments = []
            for cur_fold in range(self.n_folds):
                logger.info('> fold %d/%d' % (cur_fold+1, self.n_folds))
                dtm_train = data[self.split_folds != cur_fold, :]
                dtm_valid = data[self.split_folds == cur_fold, :]

                lda_instance = LatentDirichletAllocation(**params)
                lda_instance.fit(dtm_train)

                perpl_train = lda_instance.perplexity(dtm_train)      # evaluate "with itself"
                perpl_valid = lda_instance.perplexity(dtm_valid)      # evaluate with held-out data
                perpl_both = (perpl_train, perpl_valid)

                logger.info('> done fitting model. perplexity on training data: %f /'
                            ' on validation data: %f' % perpl_both)

                perplexity_measurments.append(perpl_both)

            results = perplexity_measurments
        else:
            logger.info('fitting LDA model from package `sklearn` to data of shape %s with parameters:'
                        ' %s' % (data.shape, params))

            lda_instance = LatentDirichletAllocation(**params)
            lda_instance.fit(data)

            results = {}
            for metric in self.eval_metric:
                if metric == 'cross_validation': continue

                metric_opt = self.eval_metric_options.get(metric, {})

                if metric == 'cao_juan_2009':
                    topic_word_distrib = lda_instance.components_ / lda_instance.components_.sum(axis=1)[:, np.newaxis]
                    res = metric_cao_juan_2009(topic_word_distrib)
                elif metric == 'arun_2010':
                    topic_word_distrib = lda_instance.components_ / lda_instance.components_.sum(axis=1)[:, np.newaxis]
                    res = metric_arun_2010(topic_word_distrib, lda_instance.transform(data), data.sum(axis=1))
                else:  # default: perplexity
                    res = lda_instance.perplexity(data)

                logger.info('> evaluation result with metric "%s": %f' % (metric, res))
                results[metric] = res

        self.send_results(params, results)


def evaluate_topic_models(varying_parameters, constant_parameters, data, metric=None, n_workers=None, n_folds=0,
                          **metric_kwargs):
    mp_eval = MultiprocEvaluation(MultiprocEvaluationWorkerSklearn, AVAILABLE_METRICS, data,
                                  varying_parameters, constant_parameters,
                                  metric=metric, metric_options=metric_kwargs,
                                  n_max_processes=n_workers, n_folds=n_folds)

    return mp_eval.evaluate()