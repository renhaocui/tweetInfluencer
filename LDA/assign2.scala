import scalanlp.io._;
import scalanlp.stage._;
import scalanlp.stage.text._;
import scalanlp.text.tokenize._;
import scalanlp.pipes.Pipes.global._;

import edu.stanford.nlp.tmt.stage._;
import edu.stanford.nlp.tmt.model.lda._;
import edu.stanford.nlp.tmt.model.llda._;

val source = CSVFile("LDA/LDAinput.csv");

val tokenizer = {
  SimpleEnglishTokenizer() ~>            // tokenize on space and punctuation
  CaseFolder() ~>                        // lowercase everything
  WordsAndNumbersOnlyFilter() ~>         // ignore non-words and non-numbers
  MinimumLengthFilter(1)                 // take terms with >=1 characters
}

val text = {
  source ~>                              // read from the source file
  Column(1) ~>                           // select column containing text
  TokenizeWith(tokenizer) ~>             // tokenize with tokenizer above
  TermCounter() ~>                       // collect counts (needed below)
  TermMinimumDocumentCountFilter(1) ~>   // filter terms in <4 docs
  DocumentMinimumLengthFilter(1)         // take only docs with >=5 terms
}

val dataset = LDADataset(text);

val params = LDAModelParams(numTopics = 20, dataset = dataset, topicSmoothing = 0.01, termSmoothing = 0.01);

val modelPath = file("LDA/TMTSnapshots");

TrainCVB0LDA(params, dataset, output=modelPath, maxIterations=1000);
